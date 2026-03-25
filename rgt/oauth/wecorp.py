

from urllib.parse import urlencode

auth_url = "https://login.work.weixin.qq.com/wwlogin/sso/login/"


params = {
    "login_type": "CorpApp",
    "appid": "ww53a723f2c5c1f05e",
    "agentid": "1000002",
    "redirect_uri": "http://172.16.40.76:5173/login"
}


f"{auth_url}?{urlencode(params)}"


ACCESS_TOKEN = "qxE7fNVSvTmSQDZNUaqdV8GKhrxmSeML1ICsnT8Pi2NFB11ns-9yhJpbrQ68CyT4oHjfAzNWbr_PbJZor1AOBJE15Re-JVmbAlmDtNA5tPkjKQwEb030KcU4Km-vO9-j5savYCiaN1pefWOKLzqxsQ5Hrdymd_ESTWNQEUDG4Lwg6cjZEYE1Ty9aLgASr-e10t-6wjJYiivJD2cinb21mA"
CODE = "x7HcAxDGNRvmF5A14nAAW_QxPfovdT3pM2QluE7_H1o"
url = f"https://qyapi.weixin.qq.com/cgi-bin/auth/getuserinfo?access_token={ACCESS_TOKEN}&code={CODE}"


url = " https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=ww53a723f2c5c1f05e&corpsecret=PlzubTginIf8x4-IhxCrWK53VbRUWYLVvvypC61OHdY"
