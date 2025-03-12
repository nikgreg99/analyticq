import os

import pytest
from analyticq.engine.core.models import (AnalyticQSASTIssueModel,
                                          AnalyticQSASTScanResultModel)
from analyticq.engine.tools import BrakemanTool
from analyticq.exception import (ScanConfigurationException,
                                 ScanTimeoutException)


@pytest.fixture(scope="module")
def brakeman_tool():
    """Initialize and configure BrakemanTool with test settings."""
    tool = BrakemanTool()
    # Reduce timeout for test environment
    return tool


@pytest.fixture(scope="module")
def sample_rails_app(tmp_path_factory):
    """Create a temporary Rails application structure with known security vulnerabilities."""
    app_dir = tmp_path_factory.mktemp("rails_app")

    # Create basic Rails app structure
    create_rails_directory_structure(app_dir)

    # Create vulnerable controller
    controllers_dir = app_dir / "app" / "controllers"
    users_controller = controllers_dir / "users_controller.rb"

    controller_code = """
class UsersController < ApplicationController
  def show
    # SQL Injection vulnerability
    @user = User.find_by("id = '#{params[:id]}'")

    # Command Injection vulnerability
    system("echo #{params[:file_name]}")

    # Cross-Site Scripting (XSS) vulnerability
    @user_input = params[:user_input]

    # Mass Assignment vulnerability
    @user = User.new(params[:user])

    # Unscoped find vulnerability
    @post = Post.find(params[:id])

    # Unsafe redirect
    redirect_to params[:redirect_url]
  end

  def create
    # CSRF protection bypass
    skip_before_action :verify_authenticity_token

    # Unsafe deserialize
    @object = YAML.load(params[:data])
  end
end
"""
    users_controller.write_text(controller_code)

    # Create model with weak password validation
    models_dir = app_dir / "app" / "models"
    user_model = models_dir / "user.rb"

    model_code = """
class User < ApplicationRecord
  # Weak password settings
  has_secure_password

  # Dangerous attr_accessible
  attr_accessible :name, :email, :admin

  # No validation for admin flag
  attr_accessor :admin
end
"""
    user_model.write_text(model_code)

    # Create vulnerable view with XSS
    views_dir = app_dir / "app" / "views" / "users"
    views_dir.mkdir(parents=True, exist_ok=True)
    show_view = views_dir / "show.html.erb"

    view_code = """
<h1>User Profile</h1>

<!-- XSS vulnerability -->
<div><%= @user_input %></div>

<!-- Unescaped output -->
<div><%= raw params[:message] %></div>

<!-- Template injection -->
<%= eval(params[:template]) %>
"""
    show_view.write_text(view_code)

    # Create routes file with suspicious routing
    config_dir = app_dir / "config"
    routes_file = config_dir / "routes.rb"

    routes_code = """
Rails.application.routes.draw do
  # Potentially dangerous catch-all route
  match ':controller/:action/:id', via: [:get, :post]

  resources :users

  # Dangerous eval route
  get 'execute/:code', to: lambda { |env|
    code = env["action_dispatch.request.path_parameters"][:code]
    eval(code)
  }
end
"""
    routes_file.write_text(routes_code)

    # Create application.rb with unsafe settings
    application_file = config_dir / "application.rb"

    application_code = """
require_relative 'boot'
require 'rails/all'

module VulnerableApp
  class Application < Rails::Application
    # Security misconfiguration
    config.action_controller.permit_all_parameters = true

    # Set default protected_from_forgery to false
    config.action_controller.allow_forgery_protection = false
  end
end
"""
    application_file.write_text(application_code)

    # Create database.yml with credentials
    database_file = config_dir / "database.yml"

    database_code = """
development:
  adapter: sqlite3
  database: db/development.sqlite3
  pool: 5
  timeout: 5000
  username: admin
  password: password123
"""
    database_file.write_text(database_code)

    return app_dir


def create_rails_directory_structure(app_dir):
    """Create the basic Rails app directory structure."""
    directories = [
        "app/assets/javascripts",
        "app/assets/stylesheets",
        "app/controllers",
        "app/models",
        "app/views",
        "app/helpers",
        "config",
        "config/initializers",
        "config/environments",
        "db",
        "lib",
        "public",
        "test"
    ]

    for directory in directories:
        os.makedirs(app_dir / directory, exist_ok=True)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_brakeman_analysis(brakeman_tool, sample_rails_app):
    try:
        # 1. Install the tool
        await brakeman_tool.install()

        # 2. Run analysis on sample Rails app
        results = await brakeman_tool.run_scan(
            codebase_path=str(sample_rails_app),
        )
        print(results)

        assert isinstance(results, AnalyticQSASTScanResultModel), "Invalid results type"

        assert "tool_name" in results.scan_metadata
        assert "metrics" in results.scan_metadata
        assert results.scan_metadata["tool_name"] == "brakeman"

        assert len(results.issues) >= 7, "Should find at least 7 security issues"

        for issue in results.issues:
            assert isinstance(issue, AnalyticQSASTIssueModel), "Invalid issue type"
            assert issue.path is not None
            assert issue.message is not None

    except ScanConfigurationException as e:
        pytest.fail(f"Configuration error: {str(e)}")
    except ScanTimeoutException as e:
        pytest.fail(f"Analysis timed out: {str(e)}")
    except Exception as e:
        pytest.fail(f"Unexpected error: {str(e)}")
