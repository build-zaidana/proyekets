"""Alias ringan ke analisis form di recon, agar impor tool konsisten.

Dipertahankan terpisah supaya penamaan tool yang dipanggil agen stabil:
`analyze_form` tinggal diimpor dari sini.
"""
from __future__ import annotations

from agent.tools.recon import Form, FormField, analyze_form

__all__ = ["Form", "FormField", "analyze_form"]
