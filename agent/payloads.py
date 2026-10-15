"""Loader katalog payload (config/payloads.yml). Payload = data, bukan kode.

Kalau file tidak ada, pakai default minimal yang sama dengan .example agar pipeline
tetap bisa diuji. Lihat DESIGN_GUIDELINES §6.4.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

_DEFAULT = {
    "sql_injection": {
        "cwe": "CWE-89",
        "boolean_true": "' OR '1'='1",
        "boolean_false": "' AND '1'='2",
        "error_probe": "'",
        "control": "normaltext",
    },
    "xss_reflected": {
        "cwe": "CWE-79",
        "probe": "<script>__dastmark__</script>",
        "marker": "__dastmark__",
        "control": "dastcontrol",
    },
    "sql_error_signatures": [
        "you have an error in your sql syntax",
        "warning: mysql",
        "unclosed quotation mark",
    ],
}


@dataclass(frozen=True)
class PayloadCatalog:
    sql_injection: dict
    xss_reflected: dict
    sql_error_signatures: tuple[str, ...] = field(default_factory=tuple)

    @classmethod
    def load(cls, path: str | Path = "config/payloads.yml") -> "PayloadCatalog":
        data = dict(_DEFAULT)
        p = Path(path)
        if p.is_file():
            try:
                import yaml  # dependensi opsional

                loaded = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
                data.update(loaded)
            except Exception:  # file rusak -> pakai default, jangan menjatuhkan worker
                pass
        return cls(
            sql_injection=data["sql_injection"],
            xss_reflected=data["xss_reflected"],
            sql_error_signatures=tuple(
                s.lower() for s in data.get("sql_error_signatures", [])
            ),
        )
