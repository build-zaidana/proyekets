"""Reporter: ubah temuan jadi laporan Markdown. Lihat DESIGN_GUIDELINES §4.

Severity diurutkan menurun lalu confidence. HTML/PDF dibangun dari sumber yang sama
(belum di sini) — Markdown dulu untuk MVP & lampiran skripsi.
"""
from __future__ import annotations

from agent.core import Finding

_SEVERITY_ORDER = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1, "Info": 0}
_CONFIDENCE_ORDER = {"High": 2, "Medium": 1, "Low": 0}

_LEGAL = (
    "Pengujian dilakukan pada sistem milik sendiri atau yang diizinkan. "
    "Penggunaan terhadap sistem pihak ketiga tanpa izin adalah ilegal."
)


def sort_findings(findings: list[Finding]) -> list[Finding]:
    return sorted(
        findings,
        key=lambda f: (
            _SEVERITY_ORDER.get(f.severity, -1),
            _CONFIDENCE_ORDER.get(f.confidence, -1),
        ),
        reverse=True,
    )


def to_markdown(target_url: str, findings: list[Finding]) -> str:
    counts: dict[str, int] = {}
    for f in findings:
        counts[f.severity] = counts.get(f.severity, 0) + 1

    lines = [
        f"# Laporan DAST — {target_url}",
        "",
        f"> {_LEGAL}",
        "",
        "## Ringkasan",
        "",
        "| Severity | Jumlah |",
        "| --- | --- |",
    ]
    for sev in ("Critical", "High", "Medium", "Low", "Info"):
        lines.append(f"| {sev} | {counts.get(sev, 0)} |")
    lines += ["", "## Temuan", ""]

    if not findings:
        lines.append("_Tidak ada temuan tervalidasi._")
    for f in sort_findings(findings):
        lines += [
            f"### [{f.severity}] {f.vuln_type}",
            f"- **Klasifikasi:** {f.cwe or 'N/A'}",
            f"- **Lokasi:** {f.location}",
            f"- **Confidence:** {f.confidence}",
            "- **Evidence:**",
            "",
            "```",
            _format_evidence(f.evidence),
            "```",
            "",
            f"- **Remediasi:** {f.remediation or 'TODO'}",
            "",
        ]
    return "\n".join(lines)


def _format_evidence(evidence: dict) -> str:
    if not evidence:
        return "(tidak ada)"
    return "\n".join(f"{k}: {v}" for k, v in evidence.items())
