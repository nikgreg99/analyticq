from analyticq.config.db_conf import Base
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


class Codebase(Base):

    __tablename__ = "codebase"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(60))
