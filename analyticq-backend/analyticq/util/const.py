
class AnalyticQConst:

    # Extension Alias
    JSON_EXTENSION: str = "json"
    YAML_EXTENSION: str = "yaml"
    YML_EXTENSION: str = "yml"

    # Path folder default configuration
    ANALYTICQ_BASE_DIR: str = ".analyticq"
    ANALYTICQ_BACKEND_FOLDER: str = "analyticq-backend"
    ANALYTICQ_CONFIG_FOLDER: str = "config"
    ANALYTICQ_REPOS_FOLDER: str = "repos"
    ANALYTICQ_SCRIPTS_FOLDER: str = "scripts"
    ANALYTICQ_TEST_FOLDER: str = "tests"
    ANALYTICQ_TEST_FILE_FOLDER: str = "test_files"

    # File path default name
    ANALYTICQ_DEFAULT_CONFIG_FILE: str = "analyticq_backend_config"
    ANALYTICQ_DEFAULT_TEST_CONFIG_FILE: str = "test_config"
    ANALYTICQ_DEFAULT_PROFILE: str = "dev"

    # Batch property config
    ANALYTICQ_MIN_BATCH_SIZE: int = 50
    ANALYTICQ_MAX_BATCH_SIZE: int = 2000
    ANALYTICQ_MIN_CONCURRENCY: int = 1
    ANALTICQ_MEMORY_USAGE_THRESHOLD: int = 0.25
    ANALYTICQ_CPU_USAGE_THRESHOLD: float = 0.75
    ANALYTICQ_DEFAULT_CPU_CORES: int = 1
    ANALYTICQ_DEFAULT_CPULOAD_BALANCE: int = 1.0
