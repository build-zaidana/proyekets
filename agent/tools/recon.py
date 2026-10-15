"""Recon pasif: kumpulkan endpoint & form dari satu halaman target.

Memakai HttpClient yang sama (ber-guardrail) — recon tidak pernah menyentuh jaringan
langsung. Crawl dibatasi dangkal (lihat MAX depth) untuk MVP.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup

from agent.tools.http_client import HttpClient


@dataclass
class FormField:
    name: str
    type: str = "text"


@dataclass
class Form:
    action: str
    method: str = "GET"
    fields: list[FormField] = field(default_factory=list)


@dataclass
class PageMap:
    url: str
    links: list[str] = field(default_factory=list)
    forms: list[Form] = field(default_factory=list)


def extract_endpoints(client: HttpClient, url: str) -> PageMap:
    """Ambil link & form dari satu halaman. Link dibatasi ke host yang sama."""
    res = client.send_http_request("GET", url)
    if not res.ok or not res.body_snippet:
        return PageMap(url=url)

    soup = BeautifulSoup(res.body_snippet, "html.parser")
    host = urlsplit(url).netloc
    links: list[str] = []
    for a in soup.find_all("a", href=True):
        full = urljoin(url, a["href"])
        if urlsplit(full).netloc == host and full not in links:
            links.append(full)

    return PageMap(url=url, links=links, forms=_parse_forms(soup, url))


def analyze_form(client: HttpClient, url: str) -> list[Form]:
    """Deteksi form (login, search, dll) beserta field-nya pada satu halaman."""
    res = client.send_http_request("GET", url)
    if not res.ok or not res.body_snippet:
        return []
    return _parse_forms(BeautifulSoup(res.body_snippet, "html.parser"), url)


def _parse_forms(soup: BeautifulSoup, base_url: str) -> list[Form]:
    forms: list[Form] = []
    for f in soup.find_all("form"):
        action = urljoin(base_url, f.get("action") or base_url)
        method = (f.get("method") or "GET").upper()
        fields = [
            FormField(name=i.get("name"), type=i.get("type", "text"))
            for i in f.find_all(("input", "textarea", "select"))
            if i.get("name")
        ]
        forms.append(Form(action=action, method=method, fields=fields))
    return forms
