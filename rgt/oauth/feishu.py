from typing import Any
from urllib.parse import urlencode

from httpx import AsyncClient
from requests import Session

from .base import SyncAuthBase, AsyncAuthBase, OAuthCredentials, OAuthUserInfo


DEFAULT_SCOPE = "contact:user.phone:readonly"
AUTH_URL = "https://open.feishu.cn/open-apis/authen/v1/authorize"
APP_ACCESS_TOKEN_URL = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal"
USER_ACCESS_TOKEN_URL = "https://open.feishu.cn/open-apis/authen/v1/oidc/access_token"
USER_INFO_URL = "https://open.feishu.cn/open-apis/authen/v1/user_info"


class _FeiShuAuthMixin:
    def generate_auth_url(self: OAuthCredentials,
                          redirect_uri: str,
                          scope: str | None = None,
                          state: str | None = None,
                          **kwargs: Any) -> str:
        params = {
            "redirect_uri": redirect_uri,
            "app_id": self.ak,
            "scope": scope or DEFAULT_SCOPE,
        }

        if state:
            params["state"] = state
        params.update(kwargs)
        return f"{AUTH_URL}?{urlencode(params)}"

    def _build_app_access_token_request(self: OAuthCredentials) -> dict[str, Any]:
        return {
            "url": APP_ACCESS_TOKEN_URL,
            "json": {"app_id": self.ak, "app_secret": self.sk}
        }

    def _parse_app_access_token(self: OAuthCredentials, result: dict[str, Any]) -> str:
        return result.get("app_access_token", "")

    def _build_user_access_token_request(self: OAuthCredentials, app_access_token: str, auth_code: str) -> dict[str, Any]:
        return {
            "url": USER_ACCESS_TOKEN_URL,
            "headers": {"Authorization": f"Bearer {app_access_token}"},
            "json": {"grant_type": "authorization_code", "code": auth_code}
        }

    def _parse_user_access_token(self: OAuthCredentials, result: dict[str, Any]) -> str:
        data = result.get("data", {})
        return data.get("access_token", "")

    def _build_user_info_request(self: OAuthCredentials, user_access_token: str) -> dict[str, Any]:
        return {
            "url": USER_INFO_URL,
            "headers": {"Authorization": f"Bearer {user_access_token}"}
        }

    def _parse_user_info(self: OAuthCredentials, result: dict[str, Any]) -> OAuthUserInfo:
        data = result.get("data", {})
        return OAuthUserInfo(
            union_id=data.get("union_id", ""),
            open_id=data.get("open_id", ""),
            nickname=data.get("name", ""),
            avatar_url=data.get("avatar_url", ""),
            phone=data.get("mobile", "")
        )


class FeiShuAuth(_FeiShuAuthMixin, SyncAuthBase):
    def get_user_info(self, auth_code: str) -> OAuthUserInfo:
        with Session() as session:
            # 1.获取app_access_token
            app_access_token_result = self._post(
                session, **self._build_app_access_token_request())
            app_access_token = self._parse_app_access_token(
                app_access_token_result)

            # 2.获取user_access_token
            user_access_token_result = self._post(
                session, **self._build_user_access_token_request(app_access_token, auth_code))
            user_access_token = self._parse_user_access_token(
                user_access_token_result)

            # 3.获取用户信息
            user_result = self._get(
                session, **self._build_user_info_request(user_access_token))
            return self._parse_user_info(user_result)


class FeiShuAsyncAuth(_FeiShuAuthMixin, AsyncAuthBase):
    async def get_user_info(self, auth_code: str) -> OAuthUserInfo:
        async with AsyncClient(timeout=self.timeout) as client:
            # 1.获取app_access_token
            app_access_token_result = await self._post(
                client, **self._build_app_access_token_request())
            app_access_token = self._parse_app_access_token(
                app_access_token_result)

            # 2.获取user_access_token
            user_access_token_result = await self._post(
                client, **self._build_user_access_token_request(app_access_token, auth_code))
            user_access_token = self._parse_user_access_token(
                user_access_token_result)

            # 3.获取用户信息
            user_result = await self._get(
                client, **self._build_user_info_request(user_access_token))
            return self._parse_user_info(user_result)
