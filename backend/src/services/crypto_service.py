"""
Module: crypto_service.py
Mục đích: Cung cấp các tiện ích mật mã học chuẩn công nghiệp:
1. Băm mật khẩu bằng Argon2id (argon2-cffi)
2. Mã hóa và giải mã đối xứng dữ liệu tin nhắn bằng AES-256-GCM (cryptography)
3. Cấp phát và xác minh chữ ký JSON Web Token (PyJWT)
"""

import os
import base64
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from argon2 import PasswordHasher, Type
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import jwt

logger = logging.getLogger("services.crypto")

load_dotenv()

# ==============================================================================
# 1. CẤU HÌNH ARGON2ID (PASSWORD HASHING)
# ==============================================================================
# Cấu hình chuẩn khuyến nghị theo OWASP 2024:
# time_cost: 3 vòng, memory_cost: 65536 KiB (64 MiB), parallelism: 4 threads
_hasher = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=4,
    hash_len=32,
    type=Type.ID  # Argon2id
)


def hash_password(password: str) -> str:
    """
    Băm mật khẩu người dùng theo chuẩn Argon2id.
    """
    return _hasher.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Xác minh mật khẩu người dùng nhập vào so với chuỗi băm trong CSDL.
    """
    try:
        return _hasher.verify(hashed_password, plain_password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False
    except Exception as e:
        logger.error(f"Lỗi không xác định khi verify password: {e}")
        return False


# ==============================================================================
# 2. CẤU HÌNH AES-256-GCM (MESSAGE ENCRYPTION)
# ==============================================================================
_RAW_MASTER_KEY = os.getenv("SERVER_MASTER_KEY", "").strip()

if _RAW_MASTER_KEY:
    try:
        _AES_KEY_BYTES = base64.b64decode(_RAW_MASTER_KEY)
        if len(_AES_KEY_BYTES) != 32:
            raise ValueError(f"SERVER_MASTER_KEY phải có độ dài 32 bytes (hiện tại: {len(_AES_KEY_BYTES)} bytes)")
    except Exception as e:
        logger.warning(f"SERVER_MASTER_KEY không hợp lệ ({e}), tự sinh key dự phòng tạm thời.")
        _AES_KEY_BYTES = AESGCM.generate_key(bit_length=256)
else:
    logger.warning("Không tìm thấy SERVER_MASTER_KEY trong .env, tự sinh key tạm thời trong RAM.")
    _AES_KEY_BYTES = AESGCM.generate_key(bit_length=256)

_aesgcm = AESGCM(_AES_KEY_BYTES)


def encrypt_text(plain_text: str) -> str:
    """
    Mã hóa chuỗi văn bản bằng thuật toán AES-256-GCM.
    Đầu ra là chuỗi Base64 có định dạng: <nonce>$<ciphertext>$<tag>
    """
    if not plain_text:
        return ""

    # Sinh 12-byte nonce ngẫu nhiên chuẩn NIST cho AES-GCM
    nonce = os.urandom(12)
    data_bytes = plain_text.encode("utf-8")

    # AESGCM trong cryptography tự động gắn 16-byte authentication tag vào cuối ciphertext
    encrypted_data = _aesgcm.encrypt(nonce, data_bytes, None)
    ciphertext = encrypted_data[:-16]
    auth_tag = encrypted_data[-16:]

    nonce_b64 = base64.b64encode(nonce).decode("utf-8")
    ct_b64 = base64.b64encode(ciphertext).decode("utf-8")
    tag_b64 = base64.b64encode(auth_tag).decode("utf-8")

    return f"{nonce_b64}${ct_b64}${tag_b64}"


def decrypt_text(encrypted_payload: str) -> str:
    """
    Giải mã chuỗi văn bản đã được mã hóa bởi AES-256-GCM.
    Nếu giải mã thất bại hoặc chuỗi bị giả mạo, ném ra ngoại lệ hoặc trả về rỗng.
    """
    if not encrypted_payload:
        return ""

    try:
        parts = encrypted_payload.split("$")
        if len(parts) != 3:
            # Fallback nếu chuỗi không phải định dạng nonce$ct$tag (dữ liệu cũ chưa mã hóa)
            return encrypted_payload

        nonce = base64.b64decode(parts[0])
        ciphertext = base64.b64decode(parts[1])
        auth_tag = base64.b64decode(parts[2])

        # Ghép lại ciphertext + tag cho hàm decrypt của AESGCM
        combined = ciphertext + auth_tag
        decrypted_bytes = _aesgcm.decrypt(nonce, combined, None)
        return decrypted_bytes.decode("utf-8")
    except Exception as e:
        logger.error(f"Lỗi giải mã AES-256-GCM: {e}")
        return "[Nội dung không thể giải mã do sai khóa hoặc dữ liệu bị sửa đổi]"


# ==============================================================================
# 3. CẤU HÌNH JWT (JSON WEB TOKEN)
# ==============================================================================
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "default-dev-secret-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Cấp phát JWT Access Token với thời hạn xác định.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Giải mã và kiểm tra tính hợp lệ của JWT Access Token.
    Trả về payload nếu hợp lệ, None nếu token hết hạn hoặc sai chữ ký.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError as e:
        logger.debug(f"JWT Token không hợp lệ: {e}")
        return None
