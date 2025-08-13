import hashlib
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Hash import HMAC, SHA256

class ModelEncrypter:
    """模型加密与解密工具"""
    def __init__(self, key: str) -> None:
        """
        使用一个字符串密钥初始化加密器。
        密钥会被哈希以生成一个固定长度的加密密钥。
        """
        self.key = self._hash_key(key)  # 生成 16 字节的 AES 密钥

    def encrypt(self, model_path: str) -> str:
        """
        加密模型文件并保存为 .secret 文件。
        返回加密后的文件路径。
        """
        # 1. 加载模型数据
        model_data = self._load_file(model_path)
        
        # 2. 使用 AES-CBC 加密模型数据
        cipher = AES.new(self.key, AES.MODE_CBC)
        iv = cipher.iv  # 生成一个随机的16字节IV
        
        # 对数据进行填充以满足AES块大小
        padded_data = pad(model_data, AES.block_size)
        encrypted_model = cipher.encrypt(padded_data)

        # 3. 准备用于HMAC校验的数据 (IV + 密文)
        data_to_auth = iv + encrypted_model

        # 4. 生成 HMAC-SHA256 校验码
        hmac = HMAC.new(self.key, digestmod=SHA256)
        hmac.update(data_to_auth)
        hmac_digest = hmac.digest()

        # 5. 拼接最终数据 (IV + 密文 + HMAC)
        final_data = data_to_auth + hmac_digest

        # 6. 保存加密文件
        secret_path = self._get_secret_path(model_path)
        self._save_file(secret_path, final_data)
        print(f"✅ Encryption successful. Model saved to: {secret_path}")
        return secret_path

    def decrypt(self, secret_path: str) -> bytes:
        """
        解密 .secret 文件并返回模型数据的字节流。
        如果HMAC校验失败，会抛出 ValueError。
        """
        # 1. 加载加密文件数据
        encrypted_data_with_hmac = self._load_file(secret_path)

        # 2. 分离 HMAC 和实际加密数据
        hmac_digest = encrypted_data_with_hmac[-32:]
        data_to_auth = encrypted_data_with_hmac[:-32]

        # 3. 校验 HMAC
        hmac = HMAC.new(self.key, digestmod=SHA256)
        hmac.update(data_to_auth)
        hmac.verify(hmac_digest)  # 若校验失败将抛出异常
        print("✅ HMAC verification successful. Data integrity confirmed.")

        # 4. 分离 IV 和密文
        iv = data_to_auth[:AES.block_size]
        encrypted_model = data_to_auth[AES.block_size:]

        # 5. 解密模型数据
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted_padded_data = cipher.decrypt(encrypted_model)
        
        # 6. 去除填充
        model_data = unpad(decrypted_padded_data, AES.block_size)
        print("✅ Decryption successful. Model data extracted.")
        return model_data

    @staticmethod
    def _hash_key(key: str) -> bytes:
        """使用 SHA-256 哈希输入密钥，并截取前16字节作为AES密钥。"""
        # 使用 SHA-256 保证即使输入很短，也能生成足够长的哈希值
        sha_signature = hashlib.sha256(key.encode()).digest()
        return sha_signature[:16]  # AES-128 需要16字节的密钥

    @staticmethod
    def _load_file(path: str) -> bytes:
        """以二进制模式读取文件。"""
        with open(path, 'rb') as f:
            return f.read()

    @staticmethod
    def _get_secret_path(path: str) -> str:
        """生成加密文件的路径，后缀改为 .secret。"""
        return str(Path(path).with_suffix('.secret'))

    @staticmethod
    def _save_file(path: str, data: bytes) -> None:
        """以二进制模式写入文件。"""
        with open(path, 'wb') as f:
            f.write(data)
