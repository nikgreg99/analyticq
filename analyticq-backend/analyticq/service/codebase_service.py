from git import Repo
from git.exc import InvalidGitRepositoryError


class CodebaseService:

    @staticmethod
    def get_latest_commit_hash(repo_path: str) -> str:
        """
        Retrieve the latest commit hash for a given repository path.

         Args:
            repo_path (str): Path to the local git repository

         Returns:
            str: Full SHA-1 hash of the latest commit
        """
        try:
            repo = Repo(repo_path)
            return repo.head.commit.hexsha
        except InvalidGitRepositoryError:
            raise ValueError(f"Invalid git repository at {repo_path}")
        except Exception as e:
            raise RuntimeError(f"Error retrieving commit hash: {str(e)}")
