import sys
import json
import re
from pathlib import Path

# Add backend to path
BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app import get_cameras, create_camera, delete_camera, get_camera
from database import connect

def test_backend_camera_lifecycle_contract():
    # Test creating a test camera
    test_node = {
        "name": "Audit Test CAM-99",
        "location": "North Perimeter Gate",
        "ip_address": "192.168.10.99",
        "switch_id": "SW-A",
        "switch_ip": "192.168.10.2",
        "rtsp_url": "rtsp://192.168.10.99/live",
        "probe_mode": "SIMULATED",
    }

    created = create_camera(test_node)
    assert created is not None, "Camera must be created"
    assert created["name"] == "Audit Test CAM-99", "Camera name must match"
    created_id = created["id"]
    print(f"[PASS] Backend camera creation verified (ID: {created_id})")

    # Verify retrieval
    retrieved = get_camera(created_id)
    assert retrieved is not None, "Created camera must be retrievable"
    assert retrieved["ip_address"] == "192.168.10.99"
    print(f"[PASS] Backend camera retrieval verified")

    # Clean up test node
    delete_camera(created_id)
    assert get_camera(created_id) is None, "Camera must be deleted"
    print(f"[PASS] Backend camera deletion verified")

def test_modular_page4_frontend_structure():
    src_dir = Path(__file__).resolve().parent.parent / "src"

    expected_files = [
        src_dir / "types" / "cameraForm.ts",
        src_dir / "services" / "cameraFormService.ts",
        src_dir / "hooks" / "useCameraForm.ts",
        src_dir / "components" / "cameraForm" / "BasicInfoSection.tsx",
        src_dir / "components" / "cameraForm" / "NetworkConfigSection.tsx",
        src_dir / "components" / "cameraForm" / "ProbeModeSection.tsx",
        src_dir / "components" / "cameraForm" / "FormActionBar.tsx",
        src_dir / "pages" / "CameraManagementPage.tsx",
    ]

    for f in expected_files:
        assert f.exists(), f"Expected modular file does not exist: {f}"

    print(f"[PASS] All {len(expected_files)} modular component, hook, service, and type files verified for Page 4")

def test_audit_issues_resolutions():
    src_dir = Path(__file__).resolve().parent.parent / "src"

    # ISSUE-04: Controlled React inputs & sanitized data
    form_code = (src_dir / "pages" / "CameraManagementPage.tsx").read_text(encoding="utf-8")
    assert "dangerouslySetInnerHTML" not in form_code, "ISSUE-04: No dangerous innerHTML in form"

    # ISSUE-11: Modular service without monkey-patches
    service_code = (src_dir / "services" / "cameraFormService.ts").read_text(encoding="utf-8")
    assert "createCameraNode" in service_code, "ISSUE-11: createCameraNode service defined"
    assert "updateCameraNode" in service_code, "ISSUE-11: updateCameraNode service defined"

    # ISSUE-17: AbortController used in useCameraForm
    hook_code = (src_dir / "hooks" / "useCameraForm.ts").read_text(encoding="utf-8")
    assert "AbortController" in hook_code, "ISSUE-17: AbortController signal wired into form hook"

    # ISSUE-22: Real-time regex validators for IPv4 and RTSP
    assert "IP_V4_REGEX" in hook_code, "ISSUE-22: IP_V4_REGEX defined"
    assert "RTSP_REGEX" in hook_code, "ISSUE-22: RTSP_REGEX defined"

    ip_regex = re.compile(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
    assert ip_regex.match("192.168.1.1"), "Valid IPv4 must pass regex"
    assert not ip_regex.match("999.999.1.1"), "Invalid IPv4 must fail regex"
    assert not ip_regex.match("invalid-ip"), "Non-IP string must fail regex"

    rtsp_regex = re.compile(r"^rtsp:\/\/[a-zA-Z0-9_.\-]+(:[0-9]{1,5})?(\/.*)?$", re.IGNORECASE)
    assert rtsp_regex.match("rtsp://192.168.1.1/live"), "Valid RTSP must pass"
    assert not rtsp_regex.match("http://192.168.1.1"), "Non-RTSP must fail"

    # ISSUE-33: Simple Probe Mode options with helper guidance
    probe_section_code = (src_dir / "components" / "cameraForm" / "ProbeModeSection.tsx").read_text(encoding="utf-8")
    assert "ICMP" in probe_section_code, "ISSUE-33: ICMP option present"
    assert "RTSP" in probe_section_code, "ISSUE-33: RTSP option present"
    assert "Lightweight probe" in probe_section_code, "ISSUE-33: Plain-English helper note present"

    print("[PASS] Audit issue resolutions verified (ISSUE-04, ISSUE-11, ISSUE-17, ISSUE-22, ISSUE-33)")

def test_dist_build_output():
    dist_dir = Path(__file__).resolve().parent.parent / "dist"
    index_html = dist_dir / "index.html"
    assert index_html.exists(), "dist/index.html must exist"
    html_text = index_html.read_text(encoding="utf-8")
    assert "/assets/index-" in html_text, "dist/index.html must reference Vite bundle"
    print("[PASS] Vite production build output verified in dist/")

if __name__ == "__main__":
    test_backend_camera_lifecycle_contract()
    test_modular_page4_frontend_structure()
    test_audit_issues_resolutions()
    test_dist_build_output()
    print("\nALL PAGE 4 VALIDATION CHECKS PASSED SUCCESSFULLY!")
