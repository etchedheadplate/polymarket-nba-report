from typing import Any

from src.service.reports.selector import select_report


def create_report(payload: dict[str, Any]) -> dict[str, Any]:
    name, query_payload = payload["name"], payload["query"]
    report_cls, query_cls = select_report(name)
    query = query_cls(**query_payload)
    report = report_cls(query)
    report.make_report()
    visuals = [str(p) for p in report.visuals]
    summary = str(report.summary)
    return {"visuals": visuals, "summary": summary}
