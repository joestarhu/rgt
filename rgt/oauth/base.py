from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Protocol

from httpx import AsyncClient
from requests import Session


@dataclass(slots=True)
class OAuthUserInfo:
    union_id: str = ""
    open_id: str = ""
    nickname: str = ""
    avatar_url: str = ""
    phone: str = ""


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
                          **kwargs: Any
                          ) -> str:
        raise NotImplementedError


class SyncAuthBase(OAuthBase):
    def _request(self, session: Session, method: str, **kwargs: Any) -> dict[str, Any]:
        try:
            resp = session.request(method, timeout=self.timeout, **kwargs)
            resp.raise_for_status()
            data = resp.json()
        except:
            raise

        return data

    def _post(self, session: Session, **kwargs) -> dict[str, Any]:
        return self._request(session, "POST", **kwargs)

    def _get(self, session: Session, **kwargs) -> dict[str, Any]:
        return self._request(session, "GET", **kwargs)

    @abstractmethod
    def get_user_info(self, auth_code: str) -> OAuthUserInfo:
        raise NotImplementedError


class AsyncAuthBase(OAuthBase):
    async def _request(self, client: AsyncClient, method: str, **kwargs) -> dict[str, Any]:
        try:
            resp = await client.request(method=method, **kwargs)
            resp.raise_for_status()
            data = resp.json()
        except:
            raise

        return data

    async def _post(self, client: AsyncClient, **kwargs) -> dict[str, Any]:
        return await self._request(client, "POST", **kwargs)

    async def _get(self, client: AsyncClient, **kwargs) -> dict[str, Any]:
        return await self._request(client, "GET", **kwargs)

    @abstractmethod
    async def get_user_info(self, auth_code: str) -> OAuthUserInfo:
        raise NotImplementedError
