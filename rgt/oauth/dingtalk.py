from .base import SyncAuthBase, AsyncAuthBase, OAuthCredentials, OAuthUserInfo
from typing import Any
from urllib.parse import urlencode
from requests import Session
from httpx import AsyncClient


DEFAULT_SCOPE = "openid"
AUTH_URL = "https://login.dingtalk.com/oauth2/auth"
USER_ACCESS_TOKEN_URL = "https://api.dingtalk.com/v1.0/oauth2/userAccessToken"
USER_INFO_URL = "https://api.dingtalk.com/v1.0/contact/users/me"


class DingTalkAuthSupport:
    def generate_auth_url(self: OAuthCredentials,
                          redirect_uri: str,
                          scope: str | None = None,
                          state: str | None = None,
                          **kw) -> str:
        params = {
            "redirect_uri": redirect_uri,
            "client_id": self.ak,
            "scope": scope or DEFAULT_SCOPE,
            "response_type": "code",
            "prompt": "consent",
        }

        if state:
            params |= {"state": state}

        params |= kw
        return f"{AUTH_URL}?{urlencode(params)}"

    def get_access_token_params(self: OAuthCredentials, auth_code: str) -> dict[str, Any]:
        return {
            "url": USER_ACCESS_TOKEN_URL,
            "json": {
                "clientId": self.ak,
                "clientSecret": self.sk,
                "code": auth_code,
                "grantType": "authorization_code"
            }
        }

    def get_user_info_params(self: OAuthCredentials, access_token: str) -> dict[str, Any]:
        return {
            "url": USER_INFO_URL,
            "headers": {"x-acs-dingtalk-access-token": f"{access_token}"},
        }

    def parse_access_token(self: OAuthCredentials, result: dict) -> str:
        return result.get("accessToken", "")

    def parse_user_info(self, result: dict) -> OAuthUserInfo:
        phone_number = result.get("mobile", "")
        phone_code = result.get("stateCode", "")

        if phone_number and phone_code:
            phone = f"+{phone_code}{phone_number}"
        else:
            phone = ""

        return OAuthUserInfo(
            union_id=result.get("unionId", ""),
            open_id=result.get("openId", ""),
            nickname=result.get("nick", ""),
            avatar_url=result.get("avatarUrl", ""),
            phone=phone
        )


class DingTalkAuth(DingTalkAuthSupport, SyncAuthBase):
    def get_user_info(self, auth_code: str) -> OAuthUserInfo:
        with Session() as s:
            result = self._post(s, **self.get_access_token_params(auth_code))
            access_token = self.parse_access_token(result)

            result = self._get(s, **self.get_user_info_params(access_token))
            user_info = self.parse_user_info(result)

        return user_info


class DingTalkAsyncAuth(DingTalkAuthSupport, AsyncAuthBase):
    async def get_user_info(self, auth_code: str) -> OAuthUserInfo:
        async with AsyncClient(timeout=self.timeout) as client:
            result = await self._post(client, **self.get_access_token_params(auth_code))
            access_token = self.parse_access_token(result)

            result = await self._get(client, **self.get_user_info_params(access_token))
            user_info = self.parse_user_info(result)

        return user_info
