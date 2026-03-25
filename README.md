# Really Good Things(RGT)
> 这是一个Python的工具包,封装了一些常用的函数


# 安装初始化
```bash
uv add really-good-things
或
pip install really-good-things
```

# Security模块

```python
from rgt.security import HashUtils,JWTManager,AESECBManager

# Hash加密,比如用于密码储存和验证
password = "password"
hashed = HashUtils.hash(password)
HashUtils.verify(password,hashed)

# 生成和解密JWT
jwt_key = "IbFj9EMYb01U3kSx4R64Pb0Sb60MDkCWLkUEibC821w="
exp_min = 60
jwt_obj = JWTManager(jwt_key,exp_min)
token = jwt_obj.encode(user_id=1234567890)
payload = jwt_obj.decode(token)


# 对称加密,比如 用于存储手机号这类信息,仍需要解密成原文的.
aes_key = "62hQWMlw0uLRC2Iw/ojbtw=="
phone = "13198765432"
aes_ecb_obj = AESECBManager(aes_key)
phone_enc = aes_ecb_obj.encrypt(phone)
phone_dec = aes_ecb_obj.decrypt(phone_enc)

```


# Oauth模块
```python
from rgt.oauth import DingTalkAuth, DingTalkAsyncAuth, FeiShuAuth, FeiShuAsyncAuth
from asyncio import run


# 钉钉同步Oauth认证,
client_id="dingxx......"
client_secret="............."
d = DingTalkAuth(client_id,client_secret)
d.generate_auth_url("http://127.0.0.1:8080")
d.get_user_info("auth_code")

# 钉钉异步Oauth认证
client_id="dingxx......"
client_secret="............."
d = DingTalkAsyncAuth(ding_client_idak,client_secret)
d.generate_auth_url("http://127.0.0.1:8080")
run(d.get_user_info("auth_code"))


# 飞书同步Oauth认证
app_id="cli_xxxx......"
app_secret="............."
d = FeiShuAuth(app_id,app_secret)
d.generate_auth_url("http://127.0.0.1:8080")
d.get_user_info("auth_code")


# 飞书异步Oauth认证
app_id="cli_xxxx......"
app_secret="............."
d = FeiShuAsyncAuth(app_id,app_secret)
d.generate_auth_url("http://127.0.0.1:8080")
run(d.get_user_info("auth_code"))




```