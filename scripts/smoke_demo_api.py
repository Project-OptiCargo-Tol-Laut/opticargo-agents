"""Repeatable black-box smoke for the OptiCargo Agents demo routes."""

from __future__ import annotations

import argparse
import json
import os
from urllib.request import Request, urlopen


def call(base_url: str, token: str, payload: dict[str, object]) -> dict:
    request = Request(
        f"{base_url.rstrip('/')}/internal/v1/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "content-type": "application/json",
            "x-internal-service-token": token,
        },
        method="POST",
    )
    with urlopen(request, timeout=75) as response:
        return json.load(response)


def summarize(case: str, result: dict) -> dict[str, object]:
    data = result.get("data") or {}
    citations = data.get("citations") or []
    return {
        "case": case,
        "ok": result.get("ok"),
        "intent": data.get("intent"),
        "answer_available": data.get("answer_available"),
        "abstained": data.get("abstained"),
        "abstention_reason": data.get("abstention_reason"),
        "requires_human_confirmation": data.get("requires_human_confirmation"),
        "citation_titles": [item.get("title") for item in citations],
        "answer": data.get("answer"),
        "route": data.get("route"),
        "trace_nodes": [item.get("node") for item in data.get("trace") or []],
    }


def passed(item: dict[str, object]) -> bool:
    case = item["case"]
    expected_intent = {
        "regulation_ood": "regulation",
        "matching_invalid_voyage": "matching",
    }.get(str(case), case)
    common = item["ok"] is True and item["intent"] == expected_intent
    if case == "regulation":
        titles = item["citation_titles"]
        return bool(
            common
            and item["answer_available"] is True
            and titles
            and len(set(titles)) == 1
        )
    if case == "regulation_ood":
        return bool(common and item["abstained"] is True and not item["citation_titles"])
    if case == "matching":
        return bool(
            common
            and item["answer_available"] is True
            and item["requires_human_confirmation"] is True
            and not item["citation_titles"]
        )
    if case == "matching_invalid_voyage":
        return bool(common and item["abstained"] is True and not item["citation_titles"])
    return bool(common and item["answer_available"] is True and not item["citation_titles"])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument(
        "--voyage-id",
        default="18b35b49-f57e-4730-aa86-72473074aef5",
    )
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    token = os.environ.get("INTERNAL_SERVICE_TOKEN")
    if not token:
        raise SystemExit("INTERNAL_SERVICE_TOKEN is required")

    cases = [
        (
            "regulation",
            {
                "query": "Jelaskan persyaratan karantina untuk pengiriman hewan ikan dan tumbuhan melalui pelabuhan.",
                "requested_intent": "regulation",
            },
        ),
        (
            "route",
            {
                "query": "Jelaskan rute voyage ini.",
                "requested_intent": "route",
                "voyage_id": args.voyage_id,
            },
        ),
        (
            "matching",
            {
                "query": "Rekomendasikan muatan balik Kopra untuk voyage ini.",
                "requested_intent": "matching",
                "voyage_id": args.voyage_id,
                "commodity": "Kopra",
            },
        ),
        (
            "analytics",
            {
                "query": "Buat ringkasan analitik kandidat muatan.",
                "requested_intent": "analytics",
                "voyage_id": args.voyage_id,
            },
        ),
        (
            "regulation_ood",
            {
                "query": "Bagaimana resep rendang paling enak?",
                "requested_intent": "regulation",
            },
        ),
        (
            "matching_invalid_voyage",
            {
                "query": "Rekomendasikan muatan balik untuk voyage yang tidak ada.",
                "requested_intent": "matching",
                "voyage_id": "00000000-0000-0000-0000-000000000001",
                "commodity": "Kopra",
            },
        ),
    ]
    results = [summarize(name, call(args.base_url, token, payload)) for name, payload in cases]
    for item in results:
        item["passed"] = passed(item)
    passed_count = sum(item["passed"] is True for item in results)
    report = {
        "case_count": len(results),
        "passed_count": passed_count,
        "pass_rate": passed_count / len(results),
        "results": results,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2, default=str))
    return 1 if args.strict and passed_count != len(results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
