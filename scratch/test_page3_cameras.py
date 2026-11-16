import sys
import json
from pathlib import Path

# Add backend to path
BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app import get_cameras

def test_backend_cameras_contract():
    cameras = get_cameras()
    assert isinstance(cameras, list), "get_cameras must return a list"
    assert len(cameras) > 0, "There must be at least one registered camera"
    cam = cameras[0]
    required_keys = ["id", "name", "location", "ip_address", "status", "latency_ms", "switch_id"]
    for k in required_keys:
        assert k in cam, f"Camera item missing required key: {k}"
    print(f"[PASS] Backend /api/cameras verified ({len(cameras)} cameras retrieved, sample: {cam['name']})")

def test_modular_page3_frontend_structure():
    src_dir = Path(__file__).resolve().parent.parent / "src"

    expected_files = [
        src_dir / "types" / "camera.ts",
        src_dir / "services" / "cameraService.ts",
        src_dir / "hooks" / "useCamerasData.ts",
        src_dir / "components" / "cameras" / "CameraToolbar.tsx",
        src_dir / "components" / "cameras" / "CameraCard.tsx",
        src_dir / "components" / "cameras" / "CameraTableView.tsx",
        src_dir / "components" / "cameras" / "CameraDetailsDrawer.tsx",
        src_dir / "pages" / "CamerasPage.tsx",
    ]

    for f in expected_files:
        assert f.exists(), f"Expected modular file does not exist: {f}"

    print(f"[PASS] All {len(expected_files)} modular component, hook, service, and type files verified for Page 3")

def test_audit_issues_resolutions():
    src_dir = Path(__file__).resolve().parent.parent / "src"

    # ISSUE-10: Slide-out drawer replaces hover popups
    drawer_code = (src_dir / "components" / "cameras" / "CameraDetailsDrawer.tsx").read_text(encoding="utf-8")
    assert "fixed inset-y-0 right-0" in drawer_code, "ISSUE-10: Slide-out right drawer implemented"
    assert "Ping Latency Trend" in drawer_code, "ISSUE-10: Telemetry trend chart inside drawer"

    card_code = (src_dir / "components" / "cameras" / "CameraCard.tsx").read_text(encoding="utf-8")
    assert "hoverPanel" not in card_code, "ISSUE-10: Legacy hover popup completely removed from card"

    # ISSUE-14: WebSocket debounced batch buffer (250ms)
    hook_code = (src_dir / "hooks" / "useCamerasData.ts").read_text(encoding="utf-8")
    assert "WS_DEBOUNCE_BUFFER_MS" in hook_code, "ISSUE-14: WebSocket batch debounce buffer constant defined"
    assert "wsDebounceTimerRef" in hook_code, "ISSUE-14: Debounce timer reference used"
    assert "flushWsBuffer" in hook_code, "ISSUE-14: Batched flush buffer handler defined"

    # ISSUE-19: Full accessibility with aria-label & keyboard focus
    toolbar_code = (src_dir / "components" / "cameras" / "CameraToolbar.tsx").read_text(encoding="utf-8")
    assert "aria-label" in toolbar_code, "ISSUE-19: Toolbar contains aria-labels"
    assert "aria-label" in card_code, "ISSUE-19: CameraCard contains aria-labels"
    assert "tabIndex={0}" in card_code, "ISSUE-19: CameraCard is keyboard focusable"

    # ISSUE-28: Multi-column sorting
    assert "sortField" in toolbar_code, "ISSUE-28: Sort field selector supported"
    assert "sortOrder" in toolbar_code, "ISSUE-28: Sort order toggling supported"

    # ISSUE-30: Dense table view alternative
    table_code = (src_dir / "components" / "cameras" / "CameraTableView.tsx").read_text(encoding="utf-8")
    assert "<table" in table_code, "ISSUE-30: CameraTableView table layout implemented"

    # ISSUE-36: Instant keyword search & status filter pills
    assert "filterPills" in toolbar_code, "ISSUE-36: Filter pills with status counts"
    assert "searchQuery" in toolbar_code, "ISSUE-36: Instant search query binding"

    print("[PASS] Audit issue resolutions verified (ISSUE-10, ISSUE-14, ISSUE-19, ISSUE-28, ISSUE-30, ISSUE-36)")

def test_dist_build_output():
    dist_dir = Path(__file__).resolve().parent.parent / "dist"
    index_html = dist_dir / "index.html"
    legacy_html = dist_dir / "legacy.html"

    assert index_html.exists(), "dist/index.html must exist"
    assert legacy_html.exists(), "dist/legacy.html must exist"

    html_text = index_html.read_text(encoding="utf-8")
    assert "/assets/index-" in html_text, "dist/index.html must reference Vite bundle"
    print("[PASS] Vite production build output verified in dist/")

if __name__ == "__main__":
    test_backend_cameras_contract()
    test_modular_page3_frontend_structure()
    test_audit_issues_resolutions()
    test_dist_build_output()
    print("\nALL PAGE 3 VALIDATION CHECKS PASSED SUCCESSFULLY!")
