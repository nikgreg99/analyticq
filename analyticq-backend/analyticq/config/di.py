from analyticq.preprocessing.input import CodebaseCloner
from analyticq.service import GitAuthService
from dependency_injector import containers, providers


class ServiceContainer(containers.DeclarativeContainer):
    config = providers.Configuration('service')
    git_auth_service = providers.Singleton(GitAuthService)


class InputContainer(containers.DeclarativeContainer):
    config = providers.Configuration('input')
    codebase_cloner = providers.Factory(
        CodebaseCloner,
        git_auth_service=ServiceContainer.git_auth_service
    )


class PreprocessingContainer(containers.DeclarativeContainer):
    config = providers.Configuration('preprocessing')
    service = providers.Container(ServiceContainer)
    input = providers.Container(
        InputContainer,
        git_auth_service=service.git_auth_service
    )


class AnalyticQContainer(containers.DeclarativeContainer):
    config = providers.Configuration('app')
    service = providers.Container(ServiceContainer)
    preprocessing = providers.Container(PreprocessingContainer)
