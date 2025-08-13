# 🛡️ 模型权重安全工具 (Secure Model Weights)

[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Cryptography](https://img.shields.io/badge/Crypto-PyCryptodome-red.svg)](https://www.pycryptodome.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

一个用于加密和解密深度学习模型权重文件（如 `.pt`, `.pth` 等）的命令行工具，基于 **AES-256-CBC** 加密和 **HMAC-SHA256** 校验，确保模型的机密性和完整性。

---

## 🤔 为什么需要加密模型？

随着深度学习的广泛应用，模型权重已成为企业的核心数字资产。未受保护的模型文件可能面临以下风险：

-   **知识产权泄露**：模型权重是大量数据和计算资源投入的结晶。泄露可能导致核心技术被窃取。
-   **恶意篡改**：模型在传输或存储时可能被篡改，植入后门或影响推理结果的准确性。
-   **访问控制**：在多用户或商业分发场景下，需要确保只有授权用户才能使用模型。

因此，对模型进行加密是保护知识产权和维护供应链安全的关键一环。

## ⚙️ 核心技术

本工具结合了两种成熟的密码学技术来提供双重保护：

1.  **AES-256-CBC (高级加密标准 - 密码块链接模式)**
    * **机密性保护**：使用对称密钥对模型文件的原始内容进行加密，防止未经授权的访问。
    * **随机性**：CBC模式引入了初始向量 (IV)，确保即使加密相同的内容，每次生成的密文也不同，增强了安全性。

2.  **HMAC-SHA256 (基于哈希的消息认证码)**
    * **完整性校验**：通过一个密钥相关的哈希值来创建一个“签名”，用于验证文件在传输或存储后是否被篡改。任何对密文的改动都会导致HMAC校验失败。

### 加密流程
`模型文件 -> AES加密 (带随机IV) -> [IV + 密文] -> 计算HMAC -> [IV + 密文 + HMAC] -> .secret 文件`

### 解密流程
`.secret 文件 -> 验证HMAC -> 验证成功 -> 使用IV进行AES解密 -> 原始模型数据`

---

## 🛠️ 安装指南

1.  **克隆项目**
    ```bash
    git clone [https://github.com/SeanWong17/Secure-Model-Weights.git](https://github.com/SeanWong17/Secure-Model-Weights.git)
    cd Secure-Model-Weights
    ```

2.  **安装依赖**
    ```bash
    pip install -r requirements.txt
    ```

---

## 📖 使用方法

本工具提供了一个简单的命令行接口（CLI），支持 `encrypt` 和 `decrypt` 两个操作。

### 加密模型 (`encrypt`)

将一个模型文件（如 `.pt`）加密成一个 `.secret` 文件。

```bash
python main.py encrypt --input <模型文件路径> --key "<你的密钥>"
```

-   **示例**：
    ```bash
    # 加密 models/dummy_model.pt 文件
    python main.py encrypt --input models/dummy_model.pt --key "my-super-secret-password-123"
    ```
    运行后，将在 `models/` 目录下生成一个 `dummy_model.secret` 文件。

### 解密模型 (`decrypt`)

将一个 `.secret` 文件解密回原始的模型数据，并保存为新文件。

```bash
python main.py decrypt --input <加密文件路径> --output <解密后文件路径> --key "<你的密钥>"
```

-   **示例**：
    ```bash
    # 解密 models/dummy_model.secret 文件
    python main.py decrypt \
      --input models/dummy_model.secret \
      --output models/decrypted_model.pt \
      --key "my-super-secret-password-123"
    ```
    如果密钥正确且文件未被篡改，将在 `models/` 目录下生成 `decrypted_model.pt` 文件。

### ⚠️ **重要安全提示**

在生产环境中，**切勿将密钥硬编码在代码或命令行历史中**。请考虑使用更安全的方式管理密钥，例如：
-   **环境变量**
-   **密钥管理服务 (KMS)** (如 AWS KMS, Azure Key Vault, Google Cloud KMS)
-   **配置文件** (并确保其访问权限受控)

---

## 作为一个库使用

您也可以在自己的 Python 项目中直接导入 `ModelEncrypter` 类。

```python
from model_crypter import ModelEncrypter
import io
import torch

# 密钥
key = "my-super-secret-password-123"
encrypter = ModelEncrypter(key=key)

# 加密
encrypted_path = encrypter.encrypt("models/dummy_model.pt")
print(f"Encrypted file saved to: {encrypted_path}")

# 解密并直接加载到内存
decrypted_bytes = encrypter.decrypt(encrypted_path)

# 将解密后的字节流加载为PyTorch模型
buffer = io.BytesIO(decrypted_bytes)
# model = torch.load(buffer) # 示例：如何从字节流加载
# print("Model loaded successfully from decrypted data.")
```
---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源。
