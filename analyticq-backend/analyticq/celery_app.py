from analyticq.manager import AnalyticQCeleryManager


def get_celery_app():
    """
    Get a configured Celery application instance.

    Returns
    -------
    celery.Celery
        A configured Celery application instance with settings from AnalyticQCeleryManager.

    Notes
    -----
    This function creates an AnalyticQCeleryManager instance, retrieves the Celery app,
    and updates its configuration with the manager's settings before returning it.
    """
    celery_manager = AnalyticQCeleryManager()
    celery_app = celery_manager.get_celery_app()
    celery_app.conf.update(celery_manager.settings.model_dump())
    return celery_app


# Need to be started indipendently from Fast API
