import sys
import json
from pathlib import Path

# Add backend to path
BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app import get_dashboard_summary

def test_backend_dashboard_summary_contract():
    summary = get_dashboard_summary()
    assert isinstance(summary, dict), "get_dashboard_summary must return a dict"
    assert "statistics" in summary, "summary must contain statistics"
    assert "health_score" in summary, "summary must contain health_score"
    assert "platform_status" in summary, "summary must contain platform_status"
    assert "ml_statistics" in summary, "summary must contain ml_statistics"
    assert "maintenance_summary" in summary, "summary must contain maintenance_summary"

    stats = summary["statistics"]
    assert "total" in stats and "online" in stats and "offline" in stats, "statistics must contain total, online, offline"
    print(f"[PASS] Backend /api/dashboard/summary verified (Health: {summary['health_score']}%, Total: {stats['total']}, Online: {stats['online']})")

def test_modular_frontend_structure():
    src_dir = Path(__file__).resolve().parent.parent / "src"
    
    expected_files = [
        src_dir / "types" / "dashboard.ts",
        src_dir / "services" / "dashboardService.ts",
        src_dir / "hooks" / "useDashboardData.ts",
        src_dir / "components" / "common" / "DonutGauge.tsx",
        src_dir / "components" / "dashboard" / "MetricKpiRow.tsx",
        src_dir / "components" / "dashboard" / "AiModelHealthWidget.tsx",
        src_dir / "components" / "dashboard" / "AiPredictionsTable.tsx",
        src_dir / "components" / "dashboard" / "RootCauseWidget.tsx",
        src_dir / "components" / "dashboard" / "AssetHealthWidget.tsx",
        src_dir / "components" / "dashboard" / "AiRecommendationsWidget.tsx",
        src_dir / "components" / "dashboard" / "RecentIncidentsWidget.tsx",
        src_dir / "pages" / "DashboardPage.tsx",
    ]

    for f in expected_files:
        assert f.exists(), f"Expected modular file does not exist: {f}"

    print(f"[PASS] All {len(expected_files)} modular component, hook, service, and type files verified")

def test_audit_issues_resolutions():
    src_dir = Path(__file__).resolve().parent.parent / "src"
    
    # ISSUE-01: No monkey patch redirects
    app_shell_code = (src_dir / "components" / "AppShell.tsx").read_text(encoding="utf-8")
    assert "originalPage" not in app_shell_code, "ISSUE-01: No monkey-patching in AppShell"
    assert "DashboardPage" in app_shell_code, "ISSUE-01: Renders DashboardPage cleanly"

    # ISSUE-02: Consolidated dashboard summary & Promise.allSettled
    hook_code = (src_dir / "hooks" / "useDashboardData.ts").read_text(encoding="utf-8")
    assert "fetchDashboardSummary" in hook_code, "ISSUE-02: Consumes unified fetchDashboardSummary"
    assert "Promise.allSettled" in hook_code, "ISSUE-02: Uses Promise.allSettled to eliminate cascade failures"

    # ISSUE-03: Zero innerHTML wipes in Dashboard
    dashboard_code = (src_dir / "pages" / "DashboardPage.tsx").read_text(encoding="utf-8")
    assert "innerHTML" not in dashboard_code, "ISSUE-03: No raw innerHTML wipes in DashboardPage"

    # ISSUE-24: AI Accuracy visual donut gauge
    ai_widget_code = (src_dir / "components" / "dashboard" / "AiModelHealthWidget.tsx").read_text(encoding="utf-8")
    assert "DonutGauge" in ai_widget_code, "ISSUE-24: Uses DonutGauge component"

    # ISSUE-25: Metric KPI row 5 cards
    kpi_code = (src_dir / "components" / "dashboard" / "MetricKpiRow.tsx").read_text(encoding="utf-8")
    assert "Total Cameras" in kpi_code, "ISSUE-25: Contains Total Cameras tile"
    assert "Total Switches" in kpi_code, "ISSUE-25: Contains Total Switches tile"
    assert "Critical Issues" in kpi_code, "ISSUE-25: Contains Critical Issues tile"
    assert "System Health" in kpi_code, "ISSUE-25: Contains System Health tile"

    # ISSUE-34: Top bar streamlined
    assert "Cluster Healthy" in app_shell_code, "ISSUE-34: Streamlined top header telemetry"

    print("[PASS] Audit issue resolutions verified (ISSUE-01, ISSUE-02, ISSUE-03, ISSUE-24, ISSUE-25, ISSUE-34)")

def test_build_artifacts():
    dist_dir = Path(__file__).resolve().parent.parent / "dist"
    index_html = dist_dir / "index.html"
    legacy_html = dist_dir / "legacy.html"
    
    assert index_html.exists(), "dist/index.html must exist"
    assert legacy_html.exists(), "dist/legacy.html must exist"
    
    html_text = index_html.read_text(encoding="utf-8")
    assert "/assets/index-" in html_text, "dist/index.html must reference Vite bundle"
    print("[PASS] Vite production build output verified in dist/")

if __name__ == "__main__":
    test_backend_dashboard_summary_contract()
    test_modular_frontend_structure()
    test_audit_issues_resolutions()
    test_build_artifacts()
    print("\nALL PAGE 2 VALIDATION CHECKS PASSED SUCCESSFULLY!")
