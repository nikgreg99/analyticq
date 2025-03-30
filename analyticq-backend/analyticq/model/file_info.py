from analyticq.manager.db_manager import Base
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class AnalyticQFileInfo(Base):
    """A class representing file information in the AnalyticQ system.
    This class models metadata about source code files, storing information like file path,
    lines of code (LOC), and file size.
    Attributes:
        id (int): Primary key identifier for the file info record.
        file_path (str): Full path to the source code file.
        loc (int): Number of lines of code in the file.
        size (int): Size of the file in bytes.
    Table name:
        analyticq_file_info
    """

    __tablename__ = "analyticq_file_info"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    loc: Mapped[str] = mapped_column(Integer, nullable=False)
    size: Mapped[int] = mapped_column(Integer, nullable=False)
