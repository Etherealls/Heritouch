"""ORM 模型包：导入即注册到 Base.metadata（create_all 依赖此副作用）。"""

from app.models.game import GameLevel, GameQuestion, GameRecord
from app.models.heritage import HeritageProject, Inheritor
from app.models.user import SysUser, UserFavorite, UserWork, WrongQuestion

__all__ = [
    "HeritageProject",
    "Inheritor",
    "SysUser",
    "UserFavorite",
    "UserWork",
    "WrongQuestion",
    "GameLevel",
    "GameQuestion",
    "GameRecord",
]
