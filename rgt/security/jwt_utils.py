from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4
from jose import jwt


class JWTManager:
    def __init__(self, key: str, exp_min: float, algorithm: str = "HS256") -> None:
        """
        实例化JWT的管理类

        Args:
            key(str):jwt加密用的秘钥,可通过openssl rand -base 32 生成
            exp_min(float): jwt的过期时间(分钟)
            algorithm(str): jwt加密算法,默认"HS256"
        """
        self._key = key
        self._exp_min = exp_min
        self._algorithm = algorithm

    @property
    def key(self) -> str:
        return self._key

    @property
    def exp_min(self) -> float:
        return self._exp_min

    @property
    def algorithm(self) -> str:
        return self._algorithm

    def encode(self, **kw) -> str:
        """
        JWT编码, 自动设置jti,iat,exp参数

        Args:
            **kw:payload参数
        """
        iat = datetime.now(tz=timezone.utc)
        exp = iat + timedelta(minutes=self.exp_min)

        payload = kw | {
            "jti": uuid4().hex,
            "iat": iat,
            "exp": exp,
        }

        return jwt.encode(
            claims=payload,
            key=self.key,
            algorithm=self.algorithm
        )

    def decode(self, token: str) -> dict[str, Any]:
        """
        JWT解码

        Args:
            token(str):json web token字符串

        """
        return jwt.decode(
            token=token,
            key=self.key,
            algorithms=self.algorithm
        )
