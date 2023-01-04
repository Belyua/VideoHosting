import ormar
from database import MainMeta


class User(ormar.Model):
    class Meta(MainMeta):
        pass

    id: int = ormar.Integer(primary_key=True)
    username: str = ormar.String(max_length=100, unique=True)
    phone: str = ormar.String(max_length=14, unique=True, nullable=True)
    email = ormar.String(index=True, unique=True, nullable=False, max_length=255)
    avatar = ormar.String(max_length=500, nullable=True)
    is_active = ormar.Boolean(default=True, nullable=False)
    is_superuser = ormar.Boolean(default=False, nullable=False)