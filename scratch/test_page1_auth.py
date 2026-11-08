import sys
import os
import json
import sqlite3
from pathlib import Path

# Add backend to path
BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from config import DATABASE_PATH, JWT_SECRET
from auth import create_token, verify_password, hash_password
from database import connect

def test_dist_artifacts():
    dist_dir = Path(__file__).resolve().parent.parent / "dist"
    index_html = dist_dir / "index.html"
    legacy_html = dist_dir / "legacy.html"
    assets_dir = dist_dir / "assets"

    assert index_html.exists(), "dist/index.html must exist"
    assert legacy_html.exists(), "dist/legacy.html must exist"
    assert assets_dir.exists(), "dist/assets must exist"

    content = index_html.read_text(encoding="utf-8")
    assert '<div id="root">' in content, "dist/index.html must have #root mounting node"
    assert '/assets/index-' in content, "dist/index.html must reference Vite bundle"

    legacy_content = legacy_html.read_text(encoding="utf-8")
    assert "loginScreen" in legacy_content, "dist/legacy.html must preserve legacy app"
    print("[PASS] Static build artifacts verified in dist/")

def test_auth_backend_contracts():
    with connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username, role, password_hash FROM users WHERE username = ?", ("admin",))
        row = cursor.fetchone()
        assert row is not None, "Admin user must exist in database"
        username, role, pwd_hash = row
        assert username == "admin"
        assert role == "ADMINISTRATOR"
        assert verify_password("Admin@1234", pwd_hash), "Admin@1234 must verify against password_hash"

    token = create_token(1, "admin", "ADMINISTRATOR")
    assert token and isinstance(token, str), "Token must be valid JWT string"
    from auth import decode_token
    payload = decode_token(token)
    assert payload is not None, "Token must decode successfully"
    assert payload.get("username") == "admin"
    assert payload.get("role") == "ADMINISTRATOR"
    print("[PASS] Database users and password verification verified")

def test_react_page1_architecture():
    src_dir = Path(__file__).resolve().parent.parent / "src"
    login_page = src_dir / "pages" / "LoginPage.tsx"
    auth_context = src_dir / "context" / "AuthContext.tsx"
    theme_context = src_dir / "context" / "ThemeContext.tsx"
    api_service = src_dir / "services" / "api.ts"

    assert login_page.exists(), "LoginPage.tsx must exist"
    assert auth_context.exists(), "AuthContext.tsx must exist"
    assert theme_context.exists(), "ThemeContext.tsx must exist"
    assert api_service.exists(), "api.ts service must exist"

    # Verify ISSUE-04: Controlled inputs, no dangerouslySetInnerHTML
    login_code = login_page.read_text(encoding="utf-8")
    assert "dangerouslySetInnerHTML" not in login_code, "ISSUE-04: No dangerous innerHTML in LoginPage"
    assert "onChange={(e) => setUsername(e.target.value)}" in login_code, "ISSUE-04: Controlled username"
    assert "onChange={(e) => setPassword(e.target.value)}" in login_code, "ISSUE-04: Controlled password"

    # Verify ISSUE-21: Theme context
    theme_code = theme_context.read_text(encoding="utf-8")
    assert "prefers-color-scheme" in theme_code, "ISSUE-21: Supports system theme preference"
    assert "localStorage" in theme_code, "ISSUE-21: Persists theme in localStorage"

    # Verify ISSUE-26: Loading indicators & field feedback
    assert "isLoading" in login_code, "ISSUE-26: Displays loading state"
    assert "animate-spin" in login_code, "ISSUE-26: Displays animated spinner"
    assert "errorMessage" in login_code, "ISSUE-26: Displays validation/error banner"

    # Verify ISSUE-31: Session expired detection
    auth_code = auth_context.read_text(encoding="utf-8")
    assert "sessionExpired" in auth_code, "ISSUE-31: Tracks session expiration"
    assert "session-expired" in auth_code, "ISSUE-31: Global session expired event listener"

    print("[PASS] React architecture and audit issue resolutions verified (ISSUE-04, ISSUE-21, ISSUE-26, ISSUE-31)")

if __name__ == "__main__":
    test_dist_artifacts()
    test_auth_backend_contracts()
    test_react_page1_architecture()
    print("\nALL PAGE 1 VALIDATION CHECKS PASSED SUCCESSFULLY!")
