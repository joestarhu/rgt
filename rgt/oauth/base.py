from abc import ABC, abstractmethod
from typing import Any, Protocol
from requests import Session
from httpx import AsyncClient


class OAuthCredentials(Protocol):
    @property
    def ak(self) -> str: ...

    @property
    def sk(self) -> str: ...


class OAuthBase(ABC):
    def __init__(self, ak: str, sk: str, timeout: float = 10.0) -> None:
        """
        三方扫码登录初始化

        Args:
            ak(str):应用的appkey
            sk(str):应用的security key
            timeout(float): API请求超时时间,单位秒,默认为10秒
        """
        self._ak = ak
        self._sk = sk
        self._timeout = timeout

    @property
    def ak(self) -> str:
        return self._ak

    @property
    def sk(self) -> str:
        return self._sk

    @property
    def timeout(self) -> float:
        return self._timeout

    @abstractmethod
    def generate_auth_url(self,
                          redirect_uri: str,
                          scope: str | None = None,
                          state: str | None = None,
                          **kw
                          ) -> str: ...


class SyncAuthBase(OAuthBase):
    def _post(self, s: Session, **kw) -> dict[str, Any]:
        rsp = s.post(**kw, timeout=self.timeout)
        return rsp.json()

    def _get(self, s: Session, **kw) -> dict[str, Any]:
        rsp = s.get(**kw, timeout=self.timeout)
        return rsp.json()

    @abstractmethod
    def get_user_info(self, auth_code: str) -> dict[str, Any]: ...


class AsyncAuthBase(OAuthBase):
    async def _post(self, client: AsyncClient, **kw) -> dict[str, Any]:
        rsp = await client.post(**kw)
        return rsp.json()

    async def _get(self, client: AsyncClient, **kw) -> dict[str, Any]:
        rsp = await client.get(**kw)
        return rsp.json()

    @abstractmethod
    async def get_user_info(self, auth_code: str) -> dict[str, Any]: ...
