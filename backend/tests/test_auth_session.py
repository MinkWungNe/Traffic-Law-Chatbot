"""
Module: test_auth_session.py
Mục đích: Bộ kiểm thử tự động (Unit & Integration Tests) cho các tính năng mới:
- Xác thực tài khoản với Argon2id & JWT
- Quản trị đa phiên hội thoại (Multi-Session)
- Mã hóa & Giải mã nội dung tin nhắn bằng AES-256-GCM
- Tác vụ quản trị Admin (Đổi mật khẩu, Khóa/Mở tài khoản, Xóa mềm)
- Ghi nhận nhật ký kiểm toán (Audit Logs)
"""

import uuid
import pytest
from starlette.testclient import TestClient
from backend.src.api.main import app
from backend.src.services.crypto_service import encrypt_text, decrypt_text, hash_password, verify_password


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_crypto_primitives():
    # 1. Test Argon2id
    pwd = "SecurePassword@2026"
    hashed = hash_password(pwd)
    assert verify_password(pwd, hashed)
    assert not verify_password("WrongPassword", hashed)

    # 2. Test AES-256-GCM
    plain_text = "Hỏi: Lỗi không bật đèn xi nhan khi chuyển làn đường bị phạt bao nhiêu?"
    encrypted = encrypt_text(plain_text)
    assert "$" in encrypted
    decrypted = decrypt_text(encrypted)
    assert decrypted == plain_text


def test_admin_and_member_lifecycle(client):
    # 1. Đăng nhập Admin
    admin_login = client.post("/api/auth/login", json={"email": "admin@vinalaw.vn", "password": "Admin@2026"})
    assert admin_login.status_code == 200
    admin_token = admin_login.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 2. Đăng ký người dùng thành viên
    test_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    reg_res = client.post("/api/auth/register", json={"email": test_email, "password": "UserPass@123"})
    assert reg_res.status_code == 201
    user_token = reg_res.json()["access_token"]
    user_id = reg_res.json()["user"]["id"]
    user_headers = {"Authorization": f"Bearer {user_token}"}

    # 3. Tạo phiên trò chuyện mới
    session_res = client.post("/api/sessions", json={"title": "Tra cứu tốc độ trên cao tốc"}, headers=user_headers)
    assert session_res.status_code == 201
    session_id = session_res.json()["id"]

    # 4. Gửi câu hỏi chat trong phiên
    chat_res = client.post(
        "/api/chat",
        json={"query": "Tốc độ tối đa trên đường cao tốc là bao nhiêu?", "session_id": session_id},
        headers=user_headers
    )
    assert chat_res.status_code == 200
    assert chat_res.json()["session_id"] == session_id

    # 5. Đọc lại chi tiết phiên và kiểm tra tin nhắn đã được giải mã chính xác
    detail_res = client.get(f"/api/sessions/{session_id}", headers=user_headers)
    assert detail_res.status_code == 200
    messages = detail_res.json()["messages"]
    assert len(messages) >= 2
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Tốc độ tối đa trên đường cao tốc là bao nhiêu?"

    # 6. Admin khóa tài khoản người dùng
    lock_res = client.patch(
        f"/api/admin/users/{user_id}/status",
        json={"is_active": False, "reason": "Tạm khóa kiểm tra"},
        headers=admin_headers
    )
    assert lock_res.status_code == 200

    # 7. Tài khoản bị khóa thử đăng nhập -> bị chặn 403
    blocked_login = client.post("/api/auth/login", json={"email": test_email, "password": "UserPass@123"})
    assert blocked_login.status_code == 403

    # 8. Admin mở khóa lại
    unlock_res = client.patch(
        f"/api/admin/users/{user_id}/status",
        json={"is_active": True},
        headers=admin_headers
    )
    assert unlock_res.status_code == 200

    # 9. Admin đổi mật khẩu mới cho người dùng
    reset_res = client.post(
        f"/api/admin/users/{user_id}/reset-password",
        json={"new_password": "NewResetPassword@789"},
        headers=admin_headers
    )
    assert reset_res.status_code == 200

    # 10. Đăng nhập lại với mật khẩu mới
    new_login = client.post("/api/auth/login", json={"email": test_email, "password": "NewResetPassword@789"})
    assert new_login.status_code == 200

    # 11. Admin xóa mềm tài khoản
    del_res = client.delete(f"/api/admin/users/{user_id}", headers=admin_headers)
    assert del_res.status_code == 200

    # 12. Kiểm tra danh sách Audit Log ghi nhận đầy đủ
    audit_res = client.get("/api/admin/audit-logs", headers=admin_headers)
    assert audit_res.status_code == 200
    assert audit_res.json()["total"] > 0
