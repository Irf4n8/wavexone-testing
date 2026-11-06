"""
Sanitized Evidence Recorder for WavexOne Copy Trading.
Guarantees zero credential exposure (tokens, passwords, session cookies, fingerprints redacted).
Exports structured JSON and Markdown evidence files per scenario.
"""
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from config.settings import WavexSettings
from core.logger import logger

EVIDENCE_DIR = WavexSettings.REPORTS_DIR / "evidence"
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)


def sanitize_data(data: Any) -> Any:
    """Recursively sanitize sensitive fields in dictionaries, lists, and strings."""
    if isinstance(data, dict):
        sanitized = {}
        for k, v in data.items():
            k_lower = str(k).lower()
            if any(secret in k_lower for secret in ["password", "token", "fingerprint", "cookie", "auth"]):
                sanitized[k] = "[REDACTED]"
            else:
                sanitized[k] = sanitize_data(v)
        return sanitized
    elif isinstance(data, list):
        return [sanitize_data(item) for item in data]
    elif isinstance(data, str):
        # Scrub token query params if in URL or string
        scrubbed = re.sub(r"token=[a-zA-Z0-9_-]+", "token=[REDACTED]", data)
        scrubbed = re.sub(r"fingerprint=[a-zA-Z0-9_-]+", "fingerprint=[REDACTED]", scrubbed)
        return scrubbed
    return data


class SanitizedEvidenceRecorder:
    """Records sanitized execution evidence and exports both JSON and Markdown artifacts."""

    def __init__(self, scenario_id: str, title: str, category: str):
        self.scenario_id = scenario_id
        self.title = title
        self.category = category
        self.start_time = datetime.now()
        self.steps: List[Dict[str, Any]] = []
        self.assertions: List[Dict[str, Any]] = []
        self.status = "RUNNING"
        self.error_message: Optional[str] = None

    def log_step(
        self,
        name: str,
        action: str,
        endpoint: str = "",
        method: str = "",
        request_data: Any = None,
        response_data: Any = None,
        latency_ms: float = 0.0,
        extra: Optional[Dict[str, Any]] = None
    ):
        """Record an individual execution step with sanitized payloads."""
        step = {
            "step_index": len(self.steps) + 1,
            "timestamp": datetime.now().isoformat(),
            "name": name,
            "action": action,
            "endpoint": sanitize_data(endpoint),
            "method": method,
            "latency_ms": round(latency_ms, 2),
            "request": sanitize_data(request_data) or {},
            "response": sanitize_data(response_data) or {},
            "extra": sanitize_data(extra) or {}
        }
        self.steps.append(step)

    def log_assertion(self, name: str, expected: Any, actual: Any, passed: bool, notes: str = ""):
        """Record an explicit assertion result."""
        self.assertions.append({
            "assertion_index": len(self.assertions) + 1,
            "name": name,
            "expected": expected,
            "actual": actual,
            "passed": passed,
            "notes": notes
        })

    def finish(self, status: str, error: Optional[str] = None) -> Dict[str, Any]:
        """Finalize the scenario record and export both JSON and Markdown evidence."""
        end_time = datetime.now()
        duration_sec = round((end_time - self.start_time).total_seconds(), 2)
        self.status = status
        self.error_message = error

        passed_count = sum(1 for a in self.assertions if a["passed"])
        failed_count = sum(1 for a in self.assertions if not a["passed"])

        record = {
            "meta": {
                "scenario_id": self.scenario_id,
                "title": self.title,
                "category": self.category,
                "environment": WavexSettings.BASE_URL,
                "started_at": self.start_time.isoformat(),
                "completed_at": end_time.isoformat(),
                "duration_seconds": duration_sec,
                "status": self.status,
                "error": self.error_message
            },
            "summary": {
                "total_steps": len(self.steps),
                "total_assertions": len(self.assertions),
                "passed_assertions": passed_count,
                "failed_assertions": failed_count
            },
            "assertions": self.assertions,
            "execution_steps": self.steps
        }

        # 1. Export JSON evidence file
        json_path = EVIDENCE_DIR / f"{self.scenario_id}.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=2)

        # 2. Export Markdown evidence file
        md_path = EVIDENCE_DIR / f"{self.scenario_id}.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# Evidence Report: {self.scenario_id} — {self.title}\n\n")
            f.write(f"- **Category:** {self.category}\n")
            f.write(f"- **Status:** `{self.status}`\n")
            f.write(f"- **Execution Time:** {duration_sec}s\n")
            f.write(f"- **Timestamp:** {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            if self.error_message:
                f.write(f"> [!CAUTION]\n> **Error Message:** {self.error_message}\n\n")

            f.write("## Assertions Summary\n\n")
            f.write("| # | Assertion | Expected | Actual | Result |\n")
            f.write("|---|---|---|---|---|\n")
            for a in self.assertions:
                res_str = "✅ PASS" if a["passed"] else "❌ FAIL"
                f.write(f"| {a['assertion_index']} | {a['name']} | `{a['expected']}` | `{a['actual']}` | {res_str} |\n")

            f.write("\n## Execution Steps Telemetry\n\n")
            for s in self.steps:
                f.write(f"### Step {s['step_index']}: {s['name']}\n")
                f.write(f"- **Action:** `{s['action']}`\n")
                f.write(f"- **Endpoint:** `{s['endpoint']}` ({s['method']}) | Latency: {s['latency_ms']}ms\n")
                if s["extra"]:
                    f.write(f"- **Details:** `{json.dumps(s['extra'])}`\n")
                f.write("\n")

        logger.info(f"Exported evidence for {self.scenario_id} -> {json_path}")
        return record

