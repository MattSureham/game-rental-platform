"""
安全工具模块
提供数据加密解密功能
"""
import base64
import hashlib
from cryptography.fernet import Fernet
from ..config import ENCRYPTION_KEY


def get_cipher():
    """获取加密解密器"""
    key = hashlib.sha256(ENCRYPTION_KEY.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(key))


def encrypt_data(data: str) -> str:
    """加密数据"""
    if not data:
        return data
    cipher = get_cipher()
    encrypted = cipher.encrypt(data.encode())
    return base64.urlsafe_b64encode(encrypted).decode()


def decrypt_data(encrypted_data: str) -> str:
    """解密数据"""
    if not encrypted_data:
        return encrypted_data
    try:
        cipher = get_cipher()
        decoded = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted = cipher.decrypt(decoded)
        return decrypted.decode()
    except Exception:
        return encrypted_data


def encrypt_wechat_id(wechat_id: str) -> str:
    """加密微信号"""
    return encrypt_data(wechat_id)


def decrypt_wechat_id(encrypted_wechat_id: str) -> str:
    """解密微信号"""
    return decrypt_data(encrypted_wechat_id)
