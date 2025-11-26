from sqlalchemy.orm import DeclarativeBase


# 定义基础ORM类 让所有模型都继承它
class Base(DeclarativeBase):
    pass
