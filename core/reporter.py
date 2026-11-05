"""
Report generator for WavexOne Automated QA runs.
Produces structured Markdown and JSON reports summarizing test execution,
follower copy/allocation accuracy, latencies, and pass/fail statistics.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from config.settings import WavexSettings
from core.logger import logger


class QAReporter:
    def __init__(self, suite_name: str = "WavexOne Social Trading QA"):
        self.suite_name = suite_name
        self.start_time = datetime.now()
        self.results: Dict[str, Any] = {
            "meta": {
                "suite": suite_name,
                "environment": WavexSettings.BASE_URL,
                "started_at": self.start_time.isoformat(),
                "completed_at": None,
                "total_orders_placed": 0,
                "passed_checks": 0,
                "failed_checks": 0,
                "success_rate_percent": 0.0
            },
            "modules": {}
        }

    def record_module_result(self, module_name: str, data: Dict[str, Any]):
        self.results["modules"][module_name] = data

    def finalize(self) -> Dict[str, Any]:
        end_time = datetime.now()
        self.results["meta"]["completed_at"] = end_time.isoformat()
        self.results["meta"]["duration_seconds"] = round((end_time - self.start_time).total_seconds(), 2)

        total_orders = 0
        total_passed = 0
        total_failed = 0

        for mod, d in self.results["modules"].items():
            orders = d.get("orders_tested", 0)
            passed = d.get("passed", 0)
            failed = d.get("failed", 0)
            total_orders += orders
            total_passed += passed
            total_failed += failed

        self.results["meta"]["total_orders_placed"] = total_orders
        self.results["meta"]["passed_checks"] = total_passed
        self.results["meta"]["failed_checks"] = total_failed
        total_checks = total_passed + total_failed
        self.results["meta"]["success_rate_percent"] = round((total_passed / total_checks * 100), 2) if total_checks > 0 else 0.0

        # Save JSON
        json_path = WavexSettings.REPORTS_DIR / "social_trading_qa_report.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2)

        # Save Markdown
        md_path = WavexSettings.REPORTS_DIR / "social_trading_qa_report.md"
        self._write_markdown(md_path)

        logger.info(f"Reports generated:\n  - {json_path}\n  - {md_path}")
        return self.results

    def _write_markdown(self, path: Path):
        meta = self.results["meta"]
        lines = []
        lines.append(f"# 🚀 WavexOne Social Trading QA Automation Report")
        lines.append(f"")
        lines.append(f"**Environment:** `{meta['environment']}`  ")
        lines.append(f"**Execution Timestamp:** `{meta['started_at']}` to `{meta['completed_at']}`  ")
        lines.append(f"**Duration:** `{meta.get('duration_seconds', 0)}s`  ")
        lines.append(f"**Total Master Orders Executed:** `{meta['total_orders_placed']}` (Constraint: 20–50 orders)  ")
        lines.append(f"**Overall Success Rate:** **`{meta['success_rate_percent']}%`**  ")
        lines.append(f"")
        lines.append(f"---")
        lines.append(f"")
        lines.append(f"## 📊 Executive Summary Matrix")
        lines.append(f"")
        lines.append(f"| Social Trading Module | Master Account | Orders Tested | Passed Checks | Failed Checks | Follower Fanout / Allocation | Result |")
        lines.append(f"| :--- | :--- | :---: | :---: | :---: | :---: | :---: |")

        for mod_name, mod in self.results["modules"].items():
            status = "✅ PASS" if mod.get("failed", 0) == 0 else "❌ FAIL"
            lines.append(f"| **{mod.get('title', mod_name)}** | `{mod.get('master', 'N/A')}` | {mod.get('orders_tested', 0)} | {mod.get('passed', 0)} | {mod.get('failed', 0)} | {mod.get('fanout_summary', 'Verified')} | **{status}** |")

        lines.append(f"")
        lines.append(f"---")
        lines.append(f"")

        for mod_name, mod in self.results["modules"].items():
            lines.append(f"## 🔍 Module Details: {mod.get('title', mod_name)}")
            lines.append(f"- **Master:** `{mod.get('master')}`")
            lines.append(f"- **Followers Tested ({len(mod.get('followers', []))}):** {', '.join(f'`{f}`' for f in mod.get('followers', []))}")
            lines.append(f"- **Orders Processed:** `{mod.get('orders_tested', 0)}`")
            lines.append(f"")
            lines.append(f"### Execution Table")
            lines.append(f"| # | Symbol | Type | Side | Master Lot | Master Order ID | Followers Synced | Sync Status | Squareoff Status |")
            lines.append(f"| :-: | :--- | :---: | :---: | :-: | :-: | :-: | :-: | :-: |")

            for item in mod.get("order_records", []):
                sym = item.get("symbol")
                side = item.get("side", "").upper()
                typ = item.get("type", "").upper()
                m_lot = item.get("lot")
                oid = item.get("master_order_id", "N/A")
                synced = item.get("followers_synced", "0/0")
                sync_st = "✅ OK" if item.get("sync_success") else "❌ FAIL"
                close_st = "✅ CLOSED" if item.get("close_success") else "❌ FAIL"
                lines.append(f"| {item.get('test_index')} | `{sym}` | {typ} | {side} | {m_lot} | `{oid}` | {synced} | {sync_st} | {close_st} |")

            lines.append(f"")
            lines.append(f"---")
            lines.append(f"")

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

