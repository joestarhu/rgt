from .base import SyncAuthBase, AsyncAuthBase, OAuthCredentials, OAuthUserInfo
from typing import Any
from requests import Session
from httpx import AsyncClient
from urllib.parse import urlencode


DEFAULT_SCOPE = "contact:user.phone:readonly"
AUTH_URL = "https://open.feishu.cn/open-apis/authen/v1/authorize"
APP_ACCESS_TOKEN_URL = "https://open.feishu.cn/open-apis/auth/v3/app_access_token/internal"
USER_ACCESS_TOKEN_URL = "https://open.feishu.cn/open-apis/authen/v1/oidc/access_token"
USER_INFO_URL = "https://open.feishu.cn/open-apis/authen/v1/user_info"


class FeiShuAuthSupport:
    def generate_auth_url(self: OAuthCredentials,
                          redirect_uri: str,
                          scope: str | None = None,
                          state: str | None = None,
                          **kw) -> str:
        params = {
            "redirect_uri": redirect_uri,
            "app_id": self.ak,
            "scope": scope or DEFAULT_SCOPE,
        }

        if state:
            params |= {"state": state}

        params |= kw
        return f"{AUTH_URL}?{urlencode(params)}"

    def get_app_access_token_params(self: OAuthCredentials) -> dict[str, Any]:
        return {
            "url": APP_ACCESS_TOKEN_URL,
            "json": {"app_id": self.ak, "app_secret": self.sk}
        }

    def get_user_access_token_params(self: OAuthCredentials, app_access_token: str, auth_code: str) -> dict[str, Any]:
        return {
            "url": USER_ACCESS_TOKEN_URL,
            "headers": {"Authorization": f"Bearer {app_access_token}"},
            "json": {"grant_type": "authorization_code", "code": auth_code}
        }

    def get_user_info_params(self: OAuthCredentials, user_access_token: str) -> dict[str, Any]:
        return {
            "url": USER_INFO_URL,
            "headers": {"Authorization": f"Bearer {user_access_token}"}
        }

    def parse_app_access_token_rsp(self, result: dict) -> str:
        return result.get("app_access_token", "")

    def parse_user_access_token_rsp(self, result: dict) -> str:
        return result["data"]["access_token"]

    def parse_user_info(self, result: dict) -> OAuthUserInfo:
        data = result.get("data", {})
        return OAuthUserInfo(
            union_id=data.get("union_id", ""),
            open_id=data.get("open_id", ""),
            nickname=data.get("name", ""),
            avatar_url=data.get("avatar_url", ""),
            phone=data.get("mobile", "")
        )


class FeiShuAuth(FeiShuAuthSupport, SyncAuthBase):
    def get_user_info(self, auth_code: str) -> OAuthUserInfo:
        with Session() as s:
            # 1.获取app_access_token
            result = self._post(
                s, **self.get_app_access_token_params()
            )
            app_access_token = self.parse_app_access_token_rsp(result)

            # 2.获取access_token
            result = self._post(
                s, **self.get_user_access_token_params(app_access_token, auth_code)
            )
            user_access_token = self.parse_user_access_token_rsp(result)

            # 3.获取用户信息
            result = self._get(
                s, **self.get_user_info_params(user_access_token),
            )
            user_info = self.parse_user_info(result)

        return user_info


class FeiShuAsyncAuth(FeiShuAuthSupport, AsyncAuthBase):
    async def get_user_info(self, auth_code: str) -> OAuthUserInfo:
        async with AsyncClient(timeout=self.timeout) as client:
            # 1.获取app_access_token
            result = await self._post(
                client,
                **self.get_app_access_token_params()
            )
            app_access_token = self.parse_app_access_token_rsp(result)

            # 2.获取access_token
            result = await self._post(
                client,
                **self.get_user_access_token_params(app_access_token, auth_code)
            )
            user_access_token = self.parse_user_access_token_rsp(result)

            # 3.获取用户信息
            result = await self._get(
                client,
                **self.get_user_info_params(user_access_token)
            )
            user_info = self.parse_user_info(result)

        return user_info
