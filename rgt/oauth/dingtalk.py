from typing import Any
from urllib.parse import urlencode

from httpx import AsyncClient
from requests import Session

from .base import SyncAuthBase, AsyncAuthBase, OAuthCredentials, OAuthUserInfo


DEFAULT_SCOPE = "openid"
AUTH_URL = "https://login.dingtalk.com/oauth2/auth"
USER_ACCESS_TOKEN_URL = "https://api.dingtalk.com/v1.0/oauth2/userAccessToken"
USER_INFO_URL = "https://api.dingtalk.com/v1.0/contact/users/me"


class _DingTalkAuthMixin:
    def generate_auth_url(self: OAuthCredentials,
                          redirect_uri: str,
                          scope: str | None = None,
                          state: str | None = None,
                          **kwargs: Any) -> str:
        params = {
            "redirect_uri": redirect_uri,
            "client_id": self.ak,
            "scope": scope or DEFAULT_SCOPE,
            "response_type": "code",
            "prompt": "consent",
        }

        if state:
            params["state"] = state

        params.update(kwargs)
        return f"{AUTH_URL}?{urlencode(params)}"

    def _build_access_token_request(self: OAuthCredentials, auth_code: str) -> dict[str, Any]:
        """构建获取访问令牌的请求参数"""
        return {
            "url": USER_ACCESS_TOKEN_URL,
            "json": {
                "clientId": self.ak,
                "clientSecret": self.sk,
                "code": auth_code,
                "grantType": "authorization_code"
            },
        }

    def _parse_access_token(self: OAuthCredentials, result: dict[str, Any]) -> str:
        """从访问令牌响应中提取访问令牌"""
        return result.get("accessToken", "")

    def _build_user_info_request(self: OAuthCredentials, access_token: str) -> dict[str, Any]:
        """构建获取用户信息的请求参数"""
        return {
            "url": USER_INFO_URL,
            "headers": {
                "x-acs-dingtalk-access-token": access_token,
            },
        }

    def _parse_user_info(self: OAuthCredentials, result: dict[str, Any]) -> OAuthUserInfo:
        phone_number = result.get("mobile", "")
        phone_code = result.get("stateCode", "")
        phone = f"+{phone_code}{phone_number}" if phone_number and phone_code else ""

        return OAuthUserInfo(
            union_id=result.get("unionId", ""),
            open_id=result.get("openId", ""),
            nickname=result.get("nick", ""),
            avatar_url=result.get("avatarUrl", ""),
            phone=phone
        )


class DingTalkAuth(_DingTalkAuthMixin, SyncAuthBase):
    def get_user_info(self, auth_code: str) -> OAuthUserInfo:
        with Session() as session:
            # 1.获取access_token
            token_result = self._post(
                session, **self._build_access_token_request(auth_code))
            access_token = self._parse_access_token(token_result)

            # 2.通过access_token获取用户信息
            user_result = self._get(
                session, **self._build_user_info_request(access_token))
            return self._parse_user_info(user_result)


class DingTalkAsyncAuth(_DingTalkAuthMixin, AsyncAuthBase):
    async def get_user_info(self, auth_code: str) -> OAuthUserInfo:
        async with AsyncClient(timeout=self.timeout) as client:
            # 1.获取access_token
            token_result = await self._post(
                client, **self._build_access_token_request(auth_code))
            access_token = self._parse_access_token(token_result)

            # 2.通过access_token获取用户信息
            user_result = await self._get(
                client, **self._build_user_info_request(access_token))
            return self._parse_user_info(user_result)
