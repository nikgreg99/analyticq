from analyticq.engine.core import AnalyticQSASToolRegistry
from fastapi import APIRouter, HTTPException, status

tool_router = APIRouter(prefix="/tools", tags=["Tool Management"])


@tool_router.get(
    "/supported-languages",
    summary="Get supported programming languages",
    responses={
        status.HTTP_200_OK: {"description": "List of supported programming languages"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal server error"}
    }
)
async def get_supported_languages():
    """
    Retrieves a list of programming languages supported by the AnalyticQ static analysis tools.

    Returns:
        dict: A dictionary containing a 'languages' key with a list of supported programming languages.
              Example:
              {
                  "languages": ["Python", "Java", "JavaScript"]
              }
    """
    try:
        return {"languages": list(AnalyticQSASToolRegistry.get_supported_languages())}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving supported languages: {str(e)}"
        )


@tool_router.get(
    "/list/all",
    summary="Get all registered tools",
    responses={
        status.HTTP_200_OK: {"description": "List of all registered tools"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal server error"}
    }
)
async def list_all_tools():
    """
    Returns a list of all registered AnalyticQ static analysis tools.

    Returns:
        dict: A dictionary containing a 'tools' key with information about all registered tools.
              Example:
              {
                  "tools": [
                      {"name": "pylint", "language": "Python"},
                      {"name": "eslint", "language": "JavaScript"}
                  ]
              }
    """
    try:
        return {"tools": AnalyticQSASToolRegistry.get_all_tools_info()}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving all tools: {str(e)}"
        )


@tool_router.get(
    "/list/{language}",
    summary="Get tools for a specific language",
    responses={
        status.HTTP_200_OK: {"description": "List of tools for the specified language"},
        status.HTTP_404_NOT_FOUND: {"description": "Language not supported"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal server error"}
    }
)
async def list_tools_for_language(language: str):
    """
    Retrieves a list of available static analysis tools for a specific programming language.

    Args:
        language (str): The programming language for which to get the available tools.

    Returns:
        dict: A dictionary containing a 'tools' key with a list of tools registered for the specified language.
              Example:
              {
                  "tools": ["pylint", "mypy", "flake8"]
              }

    Raises:
        HTTPException: If the language is not supported (404) or if there's an internal server error (500).
    """
    try:
        supported_languages = AnalyticQSASToolRegistry.get_supported_languages()
        if language.lower() not in supported_languages:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Language '{language}' is not supported."
            )
        return {"tools": AnalyticQSASToolRegistry.get_tools_for_language(language)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving tools for language '{language}': {str(e)}"
        )
