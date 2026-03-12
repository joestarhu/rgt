from base64 import b64decode, b64encode
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad


class AESECBManager:
    def __init__(self, key: str) -> None:
        """
        Args:
            key(str):秘钥,长度必须为 16,24,32
        """

        # ECB模式,加密结果固定
        self._cipher = AES.new(key.encode(), AES.MODE_ECB)

    @property
    def cipher(self):
        return self._cipher

    def encrypt(self, plain_text: str) -> str:
        """加密:pad->encrypt->b64encode
        """

        # 对明文进行补全至块大小的填充
        padded_text = pad(plain_text.encode(), AES.block_size)

        # 加密
        ciphertext = self.cipher.encrypt(padded_text)

        # 返回Base64编码的密文
        return b64encode(ciphertext).decode()

    def decrypt(self, encrypted_value: str) -> str:
        """解密:b64decode->decrypt->unpad
        """

        # 将Base64编码的密文解码为字节
        ciphertext = b64decode(encrypted_value)

        # 解密
        decrypted_text = unpad(self.cipher.decrypt(ciphertext), AES.block_size)

        # 将解密后的字节串转换回字符串
        return decrypted_text.decode()

    def phone_encrypt(self, plain_text: str) -> str:
        """加密手机号;手机号按照每3位组成一段密文,然后拼接而成;
        如:18012345678,分为 180,801,012,123,......678;
        使用AES ECB模式加密,保障同样的明文输出同样的密文,用于手机号的模糊匹配

        Args:
            plain_text:手机号明文,例如:18012345678

        Returns:
            str:加密后的手机号
        """
        if (length := len(plain_text)) == 0:
            return ""

        end_pos = max(length-3, 0)
        return ",".join([self.encrypt(plain_text[i:i+3]) for i in range(end_pos+1)])

    def phone_decrypt(self, encrypted_text: str, mask: bool = True) -> str:
        """解密手机号

        Args:
            encrypted_text:加密的手机号
            mask: 是否脱敏显示,比如180****5678        

        Returns:
            str:手机号明文
        """
        if not encrypted_text:
            return ""

        phone_array = [self.decrypt(v) for v in encrypted_text.split(",")]
        phone = "".join([phone_array[i][0]
                        for i in range(8)]) + phone_array[-1]

        if mask:
            phone = f"{phone[:3]}****{phone[7:]}"

        return phone
