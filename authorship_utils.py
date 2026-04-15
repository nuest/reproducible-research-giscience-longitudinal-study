"""Helpers for the authorship analysis in 07_authorship.ipynb.

Kept as a module so the notebook stays light for fast loading and diffing.
Nothing here should depend on notebook-global state — every function takes its
inputs as arguments and returns plain Python / pandas values.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path
from typing import TYPE_CHECKING

import requests

if TYPE_CHECKING:  # only for string-annotation resolution; no runtime import
    import pandas as pd  # noqa: F401

try:
    from pyalex import Works
except ImportError:  # keep importable in environments without pyalex
    Works = None  # type: ignore


DOI_RE = re.compile(r"(10\.\d{4,9}/[^\s?#]+)", re.IGNORECASE)
COPERNICUS_RE = re.compile(
    r"agile-giss\.copernicus\.org/articles/(\d+)/(\d+)/(\d{4})", re.IGNORECASE
)
DAGSTUHL_RE = re.compile(
    r"LIPIcs[./]GIS(?:CIENCE|cience)[./](\d{4})[./](\d+)", re.IGNORECASE
)


def extract_doi(link: str) -> str | None:
    """Return the DOI for a paper `link` value, or None if no rule matches."""
    if not isinstance(link, str) or not link.strip():
        return None
    from urllib.parse import unquote

    link = link.strip()
    m = COPERNICUS_RE.search(link)
    if m:
        vol, art, year = m.groups()
        return f"10.5194/agile-giss-{vol}-{art}-{year}"
    m = DAGSTUHL_RE.search(link)
    if m:
        year, n = m.groups()
        return f"10.4230/LIPIcs.GIScience.{year}.{n}"
    m = DOI_RE.search(unquote(link))
    if m:
        doi = m.group(1).rstrip(").,;")
        return doi.lower()
    return None


def _cache_path(base: Path, doi: str) -> Path:
    safe = doi.replace("/", "_")
    return base / f"{safe}.json"


def _norm_doi(u: str | None) -> str:
    if not u:
        return ""
    return u.replace("https://doi.org/", "").replace("http://doi.org/", "").lower().strip()


def _all_dois_for_work(work: dict) -> set[str]:
    """Collect every DOI an OpenAlex work is known under.

    OpenAlex keeps the canonical DOI on ``work["doi"]`` but many works have parallel
    hostings (preprints, repository copies, venue re-publications). Those appear in
    ``work["locations"][*]["landing_page_url"]``; we scan them for ``doi.org`` URLs
    and build the full set of DOIs this work is indexed under.
    """
    dois = set()
    top = _norm_doi(work.get("doi"))
    if top:
        dois.add(top)
    for loc in (work.get("locations") or []):
        lp = loc.get("landing_page_url") or ""
        if "doi.org" in lp:
            dois.add(_norm_doi(lp))
    return {d for d in dois if d}


def _pick_title_match(
    results: list[dict], expected_doi: str, expected_title: str, expected_year: int | None
) -> tuple[dict | None, str | None]:
    """Select an OpenAlex search result that plausibly matches the target paper.

    Returns (result, reason) or (None, None). Acceptance rules, in order:

    1. ``doi-exact`` — the candidate's primary DOI matches the expected DOI.
    2. ``doi-in-locations`` — the expected DOI appears in the candidate's
       ``locations[]`` list (parallel hostings: preprints, repositories,
       re-publications).
    3. ``title-similarity`` — title similarity >= 0.95 and publication year matches;
       candidates whose primary DOI starts with ``10.4230/`` (registered LIPIcs) are
       preferred. This is a safety net for papers whose registered DOI is absent
       from OpenAlex entirely.
    """
    target_doi = expected_doi.lower()

    exact = next((r for r in results if _norm_doi(r.get("doi")) == target_doi), None)
    if exact is not None:
        return exact, "doi-exact"

    location_hit = next(
        (r for r in results if target_doi in _all_dois_for_work(r)), None
    )
    if location_hit is not None:
        return location_hit, "doi-in-locations"

    qualified = [
        r for r in results
        if title_similarity(r.get("display_name") or r.get("title") or "", expected_title) >= 0.95
        and (expected_year is None or r.get("publication_year") == expected_year)
    ]
    if qualified:
        qualified.sort(key=lambda r: 0 if _norm_doi(r.get("doi")).startswith("10.4230/") else 1)
        return qualified[0], "title-similarity"

    return None, None


def _is_not_found(exc: Exception) -> bool:
    msg = str(exc).lower()
    return "404" in msg or "not found" in msg


def _retry(call, attempts: int = 3, base_delay: float = 1.5, label: str = ""):
    """Call ``call()`` with retries on non-404 exceptions. Returns the result, or
    raises the final exception. A 404 is returned immediately (not retried)."""
    last_exc = None
    for i in range(attempts):
        try:
            return call()
        except Exception as exc:
            last_exc = exc
            if _is_not_found(exc):
                raise
            if label:
                print(f"  openalex {label} error (attempt {i + 1}): {exc}")
            time.sleep(base_delay * (i + 1))
    raise last_exc  # type: ignore[misc]


def _save(path: Path, data: dict, sleep_s: float) -> dict:
    path.write_text(json.dumps(data))
    time.sleep(sleep_s)
    return data


_LDJSON_RE = re.compile(
    r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.DOTALL | re.IGNORECASE,
)


def _flatten_ldjson(blocks: list[str]) -> list[dict]:
    """Parse all ``<script type="application/ld+json">`` payloads and unwrap any
    ``mainEntity`` wrapper so the caller sees a flat list of schema.org objects."""
    out = []
    for raw in blocks:
        try:
            obj = json.loads(raw.strip())
        except Exception:
            continue
        for item in obj if isinstance(obj, list) else [obj]:
            if not isinstance(item, dict):
                continue
            out.append(item)
            if isinstance(item.get("mainEntity"), dict):
                out.append(item["mainEntity"])
    return out


def fetch_landing_page(
    url: str, user_agent: str, sleep_s: float = 0.1, expected_doi: str | None = None
) -> dict | None:
    """Fetch a publisher landing page and extract schema.org ``ScholarlyArticle``
    metadata from any ``<script type="application/ld+json">`` blocks.

    Returns a dict shaped like the OpenAlex fields the rest of this module expects —
    ``authorships[].author.{display_name, orcid}`` and ``title``/``display_name`` —
    or ``None`` if no usable article metadata is found.
    """
    try:
        r = requests.get(url, headers={"User-Agent": user_agent}, timeout=30)
    except requests.RequestException as exc:
        print(f"  landing-page error {url}: {exc}")
        return None
    if r.status_code != 200:
        return None
    time.sleep(sleep_s)

    items = _flatten_ldjson(_LDJSON_RE.findall(r.text))
    article = next(
        (
            it for it in items
            if it.get("@type") in ("ScholarlyArticle", "Article", "Chapter")
            and it.get("author")
        ),
        None,
    )
    if article is None:
        return None

    title = article.get("name") or article.get("headline") or ""
    authors = article.get("author") or []
    if isinstance(authors, dict):
        authors = [authors]

    authorships = []
    for a in authors:
        if not isinstance(a, dict):
            continue
        name = a.get("name") or (
            f"{a.get('givenName','').strip()} {a.get('familyName','').strip()}".strip()
        )
        if not name:
            continue
        # In schema.org "Lastname, Firstname" is common for scholarly articles.
        # We do NOT normalise here — the downstream merge normalises on use.
        orcid_raw = a.get("sameAs") or ""
        if isinstance(orcid_raw, list):
            orcid_raw = next((s for s in orcid_raw if "orcid.org" in str(s)), "")
        authorships.append({
            "author": {
                "display_name": name,
                "orcid": orcid_raw if "orcid.org" in str(orcid_raw) else None,
            }
        })

    if not authorships:
        return None

    result = {
        "title": title,
        "display_name": title,
        "authorships": authorships,
        "_recovered_via": "landing-page-jsonld",
        "_recovered_from_url": url,
    }
    if expected_doi:
        result["doi"] = f"https://doi.org/{expected_doi}"
    return result


def fetch_openalex(
    doi: str,
    cache_dir: Path,
    sleep_s: float = 0.1,
    *,
    expected_title: str | None = None,
    expected_year: int | None = None,
    landing_page_url: str | None = None,
    landing_page_user_agent: str | None = None,
) -> dict | None:
    """Fetch OpenAlex metadata for a DOI, caching the JSON on disk.

    Resolution order:

    1. Direct DOI lookup (``works/https://doi.org/{doi}``).
    2. On 404, if ``expected_title`` is provided, fall back to a title search and
       accept a candidate under the rules in :func:`_pick_title_match`.
    3. If title-search also fails and ``landing_page_url`` is provided, scrape
       schema.org JSON-LD from the publisher landing page via
       :func:`fetch_landing_page`. This covers papers whose DOI is not indexed
       by OpenAlex at all (e.g. LIPIcs DOIs where OpenAlex's ``search()`` endpoint
       is intermittently flaky).

    Returns ``{"_not_found": True}`` for hard misses and ``None`` if a transient
    API error exhausted all retries (so the caller can retry later without caching
    the failure).
    """
    if Works is None:
        raise RuntimeError("pyalex is not installed")
    path = _cache_path(cache_dir, doi)
    if path.exists():
        return json.loads(path.read_text())

    try:
        data = _retry(lambda: Works()[f"https://doi.org/{doi}"], label=doi)
        return _save(path, data, sleep_s)
    except Exception as exc:
        if not _is_not_found(exc):
            return None  # transient; don't poison the cache

    def _final_fallback() -> dict:
        if landing_page_url and landing_page_user_agent:
            lp = fetch_landing_page(
                landing_page_url, landing_page_user_agent, sleep_s, expected_doi=doi,
            )
            if lp is not None:
                return _save(path, lp, sleep_s)
        return _save(path, {"_not_found": True}, sleep_s)

    if not expected_title:
        return _final_fallback()

    def search_free():
        return Works().search(expected_title).get(per_page=10)

    def search_filter():
        return Works().filter(title={"search": expected_title}).get(per_page=10)

    results: list[dict] = []
    for searcher, label in [(search_free, "search"), (search_filter, "title.search")]:
        try:
            results = _retry(searcher, label=f"{label} {doi}") or []
        except Exception:
            results = []
        if results:
            break

    if not results:
        return _final_fallback()

    match, reason = _pick_title_match(results, doi, expected_title, expected_year)
    if match is None:
        return _final_fallback()
    match["_recovered_via"] = reason
    return _save(path, match, sleep_s)


def norm_title(s: str) -> str:
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-z0-9 ]+", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()


def openalex_title(oa: dict) -> str:
    return oa.get("title") or oa.get("display_name") or ""


def title_similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, norm_title(a), norm_title(b)).ratio()


# Unicode hyphen-like characters that should be normalised to an ASCII hyphen
# *before* the ASCII-strip step, otherwise `encode('ascii', 'ignore')` drops them
# entirely and glues the surrounding tokens together (e.g. ``Olteanu‐Raimond``
# with U+2010 would become ``olteanuraimond``).
_HYPHEN_LIKE = str.maketrans({
    "\u2010": "-",  # HYPHEN
    "\u2011": "-",  # NON-BREAKING HYPHEN
    "\u2012": "-",  # FIGURE DASH
    "\u2013": "-",  # EN DASH
    "\u2014": "-",  # EM DASH
    "\u2212": "-",  # MINUS SIGN
})


def norm_name(s: str) -> str:
    if not s:
        return ""
    s = s.translate(_HYPHEN_LIKE)
    # Strip any stray quotation marks that leaked in from source-CSV quoting.
    s = s.replace('"', "").replace("'", "")
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-z ]+", " ", s.lower())
    parts = [p for p in s.split() if len(p) > 1]
    return " ".join(sorted(parts))


def clean_orcid(v) -> str | None:
    if not v:
        return None
    m = re.search(r"(\d{4}-\d{4}-\d{4}-\d{3}[\dxX])", str(v))
    return m.group(1).upper() if m else None


def openalex_authors(oa: dict) -> list[dict]:
    out = []
    for a in oa.get("authorships", []) or []:
        author = a.get("author") or {}
        name = (author.get("display_name") or "").strip().strip('"').strip()
        if not name:
            continue
        out.append({"name": name, "orcid": clean_orcid(author.get("orcid"))})
    return out


def author_identity(orcid: str | None, name: str) -> str:
    """ORCID-first identity key; fall back to the normalised name."""
    if orcid:
        return f"orcid:{orcid}"
    return f"name:{norm_name(name)}"


def merge_name_only_identities(
    orcids: "pd.Series",
    names: "pd.Series",
    manual_resolutions: "pd.DataFrame | None" = None,
) -> "pd.Series":
    """Upgrade name-only identities to ORCID identities.

    Two sources are consulted, in order:

    1. **Algorithmic merge.** For each name-only row, if exactly one ORCID in the
       corpus has the same normalised name, the row is upgraded to that ORCID.
       When two ORCIDs share a name (genuine namesakes), the merge is skipped so
       different people aren't collapsed.
    2. **Manual resolutions.** ``manual_resolutions`` is a dataframe with at least
       columns ``name_key`` (the normalised name as produced by :func:`norm_name`)
       and ``chosen_orcid``. Rows where ``chosen_orcid`` is empty/NA/``"NONE"`` mark
       the name as deliberately unresolved and are no-ops. Manual entries override
       the algorithmic merge.

    Returns a Series of identity strings aligned to the input Series.
    """
    import pandas as pd

    if len(orcids) != len(names):
        raise ValueError("orcids and names must align")

    has_orcid = orcids.notna() & (orcids != "")

    # Algorithmic: name -> single ORCID seen across the corpus
    name_to_orcids: dict[str, set[str]] = {}
    for n, o in zip(names[has_orcid].map(norm_name), orcids[has_orcid]):
        name_to_orcids.setdefault(n, set()).add(o)
    canonical = {n: next(iter(s)) for n, s in name_to_orcids.items() if len(s) == 1}

    # Manual: name_key -> chosen_orcid (skip the explicit "NONE" markers)
    manual: dict[str, str] = {}
    if manual_resolutions is not None and not manual_resolutions.empty:
        for _, r in manual_resolutions.iterrows():
            key = str(r.get("name_key", "")).strip()
            chosen = str(r.get("chosen_orcid", "") or "").strip()
            if key and chosen and chosen.upper() != "NONE":
                manual[key] = chosen

    def _ident(row_orcid, row_name):
        if pd.notna(row_orcid) and row_orcid:
            return f"orcid:{row_orcid}"
        key = norm_name(row_name)
        if key in manual:
            return f"orcid:{manual[key]}"
        if key in canonical:
            return f"orcid:{canonical[key]}"
        return f"name:{key}"

    return pd.Series(
        [_ident(o, n) for o, n in zip(orcids, names)],
        index=orcids.index,
    )


# ---------------------------------------------------------------------------
# ORCID resolution helpers (notebook-driven, non-blocking).
#
# The workflow is a three-step loop: ``prepare_orcid_resolution`` builds a queue
# of undecided name-only identities with their candidate profiles and writes a
# CSV template; ``display_orcid_resolution`` renders that queue as rich Markdown
# with clickable DOI / ORCID links; the operator fills in ``chosen_orcid`` on
# each row of the template and calls ``apply_orcid_resolutions`` to append the
# decisions to ``data/orcid-resolutions.csv``. No ``input()`` prompt is involved,
# so the kernel is never blocked and any Jupyter frontend (JupyterLab, VS Code,
# Cursor, nbclassic) works.
# ---------------------------------------------------------------------------

ORCID_API = "https://pub.orcid.org/v3.0"


def _orcid_search(name: str, user_agent: str, rows: int = 5) -> list[dict]:
    """Search the ORCID public API for profiles matching `name`.

    `name` may be either ``"Family Given"`` (comma-separated) or a free-text full
    name. Returns the raw ``expanded-result`` list (possibly empty).
    """
    family, given = _split_name(name)
    if family and given:
        q = f'family-name:"{family}" AND given-names:"{given}"'
    else:
        q = f'"{name.strip()}"'
    headers = {"Accept": "application/json", "User-Agent": user_agent}
    r = requests.get(
        f"{ORCID_API}/expanded-search",
        params={"q": q, "rows": rows},
        headers=headers,
        timeout=30,
    )
    if r.status_code != 200:
        return []
    return r.json().get("expanded-result") or []


def _split_name(name: str) -> tuple[str, str]:
    s = (name or "").strip().strip('"').strip("'").strip()
    if "," in s:
        family, _, given = s.partition(",")
        return family.strip(), given.strip()
    parts = s.split()
    if len(parts) >= 2:
        return parts[-1], " ".join(parts[:-1])
    return s, ""


def _orcid_employments(orcid: str, user_agent: str) -> list[dict]:
    headers = {"Accept": "application/json", "User-Agent": user_agent}
    r = requests.get(f"{ORCID_API}/{orcid}/employments", headers=headers, timeout=30)
    if r.status_code != 200:
        return []
    out = []
    for grp in r.json().get("affiliation-group", []) or []:
        for s in grp.get("summaries") or []:
            e = s.get("employment-summary") or {}
            org = (e.get("organization") or {}).get("name")
            role = e.get("role-title")
            start = ((e.get("start-date") or {}).get("year") or {}).get("value")
            end_block = e.get("end-date")
            end = ((end_block or {}).get("year") or {}).get("value") if end_block else None
            out.append({"organization": org, "role": role, "start": start, "end": end})
    return out


def _orcid_cache_file(cache_dir: Path, kind: str, key: str) -> Path:
    """Resolve a filename inside ``cache_dir/orcid/{kind}/`` for a given cache key.

    The key is sanitised to the ASCII subset that's safe on every filesystem; if the
    result is longer than 120 chars, a short SHA-1 suffix is appended so long queries
    (names with many Unicode characters, for example) still round-trip.
    """
    safe = re.sub(r"[^A-Za-z0-9_\-.]", "_", key).strip("_") or "_empty"
    if len(safe) > 120:
        h = hashlib.sha1(key.encode()).hexdigest()[:8]
        safe = safe[:100] + "_" + h
    return cache_dir / "orcid" / kind / f"{safe}.json"


def _orcid_search_cached(
    name: str, user_agent: str, rows: int, cache_dir: Path | None, sleep_s: float,
) -> list[dict]:
    if cache_dir is None:
        return _orcid_search(name, user_agent, rows=rows)
    p = _orcid_cache_file(cache_dir, "search", f"rows={rows}|{name}")
    if p.exists():
        return json.loads(p.read_text())
    results = _orcid_search(name, user_agent, rows=rows)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(results))
    time.sleep(sleep_s)  # sleep only after a real API call, not on cache hits
    return results


def _orcid_employments_cached(
    orcid: str, user_agent: str, cache_dir: Path | None, sleep_s: float,
) -> list[dict]:
    if cache_dir is None:
        return _orcid_employments(orcid, user_agent)
    p = _orcid_cache_file(cache_dir, "employments", orcid)
    if p.exists():
        return json.loads(p.read_text())
    results = _orcid_employments(orcid, user_agent)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(results))
    time.sleep(sleep_s)
    return results


def _orcid_recent_works_cached(
    orcid: str, user_agent: str, n: int, cache_dir: Path | None, sleep_s: float,
) -> list[dict]:
    if cache_dir is None:
        return _orcid_recent_works(orcid, user_agent, n=n)
    p = _orcid_cache_file(cache_dir, "works", f"n={n}|{orcid}")
    if p.exists():
        return json.loads(p.read_text())
    results = _orcid_recent_works(orcid, user_agent, n=n)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(results))
    time.sleep(sleep_s)
    return results


def _orcid_recent_works(orcid: str, user_agent: str, n: int = 5) -> list[dict]:
    headers = {"Accept": "application/json", "User-Agent": user_agent}
    r = requests.get(f"{ORCID_API}/{orcid}/works", headers=headers, timeout=30)
    if r.status_code != 200:
        return []
    works = []
    for g in r.json().get("group", []) or []:
        s = (g.get("work-summary") or [{}])[0]
        title = (((s.get("title") or {}).get("title") or {}) or {}).get("value")
        year = (((s.get("publication-date") or {}).get("year") or {}) or {}).get("value")
        jt = ((s.get("journal-title") or {}) or {}).get("value") if s.get("journal-title") else None
        works.append({
            "title": title,
            "year": int(year) if year and str(year).isdigit() else None,
            "journal": jt,
        })
    works.sort(key=lambda w: w["year"] or 0, reverse=True)
    return works[:n]


def _load_decisions(path: Path) -> "pd.DataFrame":
    import pandas as pd
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame(
        columns=["name_key", "name_seen", "chosen_orcid", "candidate_orcids", "decided_at", "notes"]
    )


def _save_decisions(df: "pd.DataFrame", path: Path) -> None:
    df.to_csv(path, index=False)


def _most_recent_employment(employments: list[dict]) -> dict | None:
    if not employments:
        return None
    # Prefer ongoing (no end date); tie-break on start year.
    def k(e): return (e.get("end") is None, e.get("start") or "0")
    return sorted(employments, key=k, reverse=True)[0]


def prepare_orcid_resolution(
    authors_df: "pd.DataFrame",
    papers_df: "pd.DataFrame",
    decisions_path: Path,
    candidates_path: Path,
    user_agent: str,
    *,
    cache_dir: Path | None = None,
    only_cross_year: bool = True,
    rows_per_search: int = 5,
    sleep_s: float = 0.3,
) -> list[dict]:
    """Build the queue of undecided name-only identities, query ORCID for each,
    and write a CSV template at ``candidates_path``.

    Returns a list of dicts (one per name to review). Each dict has:
      - ``name_key`` — normalised name (the key in ``orcid-resolutions.csv``)
      - ``name_seen`` — display name as it appears on the first matching paper
      - ``n_papers`` — number of papers this identity is attached to
      - ``papers`` — list of ``{paper, year, conf, doi, title}`` for this author
      - ``candidates`` — list of ORCID profiles with ``orcid``, ``given``,
        ``family``, ``institutions``, ``employments``, ``recent_works``

    ``papers_df`` must provide at least ``paper`` and ``title`` columns (the main
    ``df`` in the notebook is fine). Titles are joined in by ``paper`` id so the
    rich display can show what this author contributed.

    Already-decided identities (present in ``decisions_path``) are omitted.
    ``only_cross_year=True`` restricts the queue to identities that appear in
    more than one year, matching the cross-conference focus of the analysis.

    If ``cache_dir`` is given, ORCID API responses (the name search plus each
    candidate's employments and recent works) are cached as JSON under
    ``cache_dir/orcid/{search,employments,works}/``. A re-run of this function
    then reads from disk instead of hitting the API again — delete the cache
    directory (or the specific file) to force a refresh. Recommended: pass the
    same ``CACHE_DIR`` the notebook uses for OpenAlex (``data/authorship-cache``).
    """
    import pandas as pd

    decisions_path = Path(decisions_path)
    candidates_path = Path(candidates_path)
    candidates_path.parent.mkdir(parents=True, exist_ok=True)

    decisions = _load_decisions(decisions_path)
    already = set(decisions["name_key"].astype(str))

    name_only = authors_df[authors_df["identity"].str.startswith("name:")].copy()
    name_only["name_key"] = name_only["identity"].str.replace("name:", "", regex=False)

    if only_cross_year:
        years_per_name = name_only.groupby("name_key")["year"].nunique()
        name_only = name_only[
            name_only["name_key"].isin(years_per_name[years_per_name > 1].index)
        ]

    aggregated = (
        name_only.groupby("name_key")
        .agg(name=("name", lambda s: sorted(set(s))[0]), n_papers=("paper", "nunique"))
        .reset_index()
        .sort_values("n_papers", ascending=False)
    )
    aggregated = aggregated[~aggregated["name_key"].isin(already)]

    title_by_paper = dict(zip(papers_df["paper"], papers_df.get("title", pd.Series(dtype=str))))
    paper_rows = name_only[["name_key", "paper", "conf", "year", "doi"]].drop_duplicates()

    items: list[dict] = []
    for _, row in aggregated.iterrows():
        key = row["name_key"]
        papers_for_name = [
            {
                "paper": r["paper"],
                "year": int(r["year"]) if pd.notna(r["year"]) else None,
                "conf": r["conf"],
                "doi": r["doi"],
                "title": title_by_paper.get(r["paper"], ""),
            }
            for _, r in paper_rows[paper_rows["name_key"] == key].iterrows()
        ]
        papers_for_name.sort(key=lambda p: (p["year"] or 0, p["conf"] or ""))

        try:
            hits = _orcid_search_cached(
                row["name"], user_agent, rows_per_search, cache_dir, sleep_s=sleep_s,
            )
        except Exception as exc:
            print(f"  ORCID search error for {row['name']!r}: {exc}")
            hits = []

        candidates = []
        for h in hits:
            orcid = h.get("orcid-id")
            if not orcid:
                continue
            try:
                emp = _orcid_employments_cached(orcid, user_agent, cache_dir, sleep_s=sleep_s)
                works = _orcid_recent_works_cached(orcid, user_agent, 5, cache_dir, sleep_s=sleep_s)
            except Exception as exc:
                print(f"  ORCID profile fetch error for {orcid}: {exc}")
                emp, works = [], []
            candidates.append({
                "orcid": orcid,
                "given": h.get("given-names") or "",
                "family": h.get("family-names") or "",
                "institutions": h.get("institution-name") or [],
                "employments": emp,
                "recent_works": works,
            })

        items.append({
            "name_key": key,
            "name_seen": row["name"],
            "n_papers": int(row["n_papers"]),
            "papers": papers_for_name,
            "candidates": candidates,
        })

    # Write the CSV template. Columns are minimal — the operator only needs
    # to fill ``chosen_orcid`` (and optionally ``notes``); ``candidate_orcids``
    # is kept so the decisions CSV retains the audit trail when we apply.
    template_rows = [
        {
            "name_key": it["name_key"],
            "name_seen": it["name_seen"],
            "n_papers": it["n_papers"],
            "candidate_orcids": ";".join(c["orcid"] for c in it["candidates"]),
            "chosen_orcid": "",
            "notes": "",
        }
        for it in items
    ]
    template_df = pd.DataFrame(
        template_rows,
        columns=["name_key", "name_seen", "n_papers", "candidate_orcids", "chosen_orcid", "notes"],
    )

    # If a template already exists, preserve any partially-filled-in values so
    # a re-run of the preparation step doesn't clobber in-progress work.
    # Read as strings so that an index like ``"1"`` survives the round-trip
    # (pandas would otherwise infer it as float and drop the preservation check).
    if candidates_path.exists():
        try:
            prior = pd.read_csv(candidates_path, dtype=str, keep_default_na=False)
            prior_by_key = prior.set_index("name_key")
            for i, r in template_df.iterrows():
                k = r["name_key"]
                if k in prior_by_key.index:
                    for col in ("chosen_orcid", "notes"):
                        if col not in prior_by_key.columns:
                            continue
                        v = str(prior_by_key.at[k, col]).strip()
                        if v:
                            template_df.at[i, col] = v
        except Exception as exc:
            print(f"  could not merge existing template {candidates_path}: {exc}")

    template_df.to_csv(candidates_path, index=False)
    return items


def display_orcid_resolution(items: list[dict], candidates_path: Path | None = None) -> None:
    """Render the resolution queue as rich Markdown with clickable DOI / ORCID links.

    For each queue item we show:

    - the author's name and number of papers in the local corpus,
    - every local paper as a clickable DOI link alongside its title,
    - every ORCID candidate as a clickable ``https://orcid.org/{orcid}`` link,
      with the candidate's institution, most-recent employment, and most-recent
      works underneath.

    The function is notebook-only: it imports ``IPython.display`` lazily and
    does nothing surprising if called from a plain interpreter. ``items`` is
    whatever :func:`prepare_orcid_resolution` returned.
    """
    try:
        from IPython.display import Markdown, display
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("display_orcid_resolution needs IPython") from exc

    if not items:
        display(Markdown(
            "*Nothing to resolve — all eligible name-only identities already "
            "have a recorded decision.*"
        ))
        return

    intro = [
        f"### ORCID resolution queue — {len(items)} name(s) to review\n",
        "For each name below, inspect the candidate ORCID profiles (links open the ",
        "public ORCID page) and the paper landing pages (DOI links), then record ",
        "your decision by editing the `chosen_orcid` column in ",
    ]
    if candidates_path is not None:
        intro.append(f"[`{candidates_path}`]({candidates_path}).\n\n")
    else:
        intro.append("the candidates CSV template.\n\n")
    intro.extend([
        "Accepted values for `chosen_orcid`:\n\n",
        "- a 1-based candidate index (`1`, `2`, ...) — easiest to type when picking from the list below,\n",
        "- a full ORCID (`0000-0001-2345-6789`) — equivalent, useful when copy-pasting from elsewhere,\n",
        "- `NONE` — explicitly record 'no match' (prevents re-querying),\n",
        "- leave blank — skip for now (row stays in the template, will re-appear on the next run).\n\n",
        "When you are done editing, run the apply cell below.",
    ])
    display(Markdown("".join(intro)))

    for item in items:
        parts = [
            f"---\n\n#### {item['name_seen']}  ",
            f"*({item['n_papers']} paper(s) in corpus; key `{item['name_key']}`)*\n\n",
            "**Papers in our corpus:**\n\n",
        ]
        for p in item["papers"]:
            doi = (p.get("doi") or "").strip()
            if doi:
                doi_md = f"[`{doi}`](https://doi.org/{doi})"
            else:
                doi_md = "*no DOI*"
            title = (p.get("title") or "").strip() or "*no title*"
            yr = p.get("year")
            conf = p.get("conf") or ""
            parts.append(f"- {yr} / {conf} — {doi_md} — *{title}*\n")
        parts.append("\n")

        candidates = item["candidates"]
        if not candidates:
            parts.append(
                "**No ORCID profiles match this name.** Record `NONE` in "
                "`chosen_orcid` to skip this identity permanently, or leave the "
                "field blank to re-query next time.\n"
            )
        else:
            parts.append(f"**ORCID candidates ({len(candidates)}):**\n\n")
            for idx, c in enumerate(candidates, start=1):
                orcid = c["orcid"]
                full = f"{c['given']} {c['family']}".strip() or "*no name*"
                parts.append(
                    f"- **`[{idx}]`** [`{orcid}`](https://orcid.org/{orcid}) — **{full}**\n"
                )
                if c["institutions"]:
                    parts.append(
                        f"    - institution(s) on profile: {', '.join(c['institutions'])}\n"
                    )
                emp = _most_recent_employment(c["employments"])
                if emp:
                    s = emp.get("organization") or "-"
                    if emp.get("role"):
                        s += f" ({emp['role']})"
                    if emp.get("start"):
                        s += f", since {emp['start']}"
                    if emp.get("end"):
                        s += f" (ended {emp['end']})"
                    parts.append(f"    - most-recent employment: {s}\n")
                if c["recent_works"]:
                    parts.append("    - most-recent works:\n")
                    for w in c["recent_works"]:
                        yr = w.get("year") or "-"
                        t = (w.get("title") or "").strip()
                        jt = f" [{w['journal']}]" if w.get("journal") else ""
                        parts.append(f"        - ({yr}) {t}{jt}\n")
                parts.append("\n")

        display(Markdown("".join(parts)))


def _resolve_chosen(chosen: str, candidate_orcids: str, key: str) -> str:
    """Map a ``chosen_orcid`` cell value to a canonical ORCID or ``NONE``.

    Accepted forms:

    - ``NONE`` (any case) -> ``"NONE"``,
    - a 1-based decimal index (``"1"``, ``"2"``, ...) -> the corresponding entry of
      the semicolon-joined ``candidate_orcids`` column,
    - a syntactically valid ORCID (any case) -> the canonicalised ORCID.

    Anything else raises :class:`ValueError` so a typo can't be silently recorded
    as a decision.
    """
    chosen = chosen.strip()
    if chosen.upper() == "NONE":
        return "NONE"
    if chosen.isdigit():
        candidates = [c.strip() for c in (candidate_orcids or "").split(";") if c.strip()]
        idx = int(chosen)
        if not candidates:
            raise ValueError(
                f"chosen_orcid={chosen!r} for {key!r} is a candidate index but "
                "candidate_orcids is empty (no ORCID profiles were found for this "
                "name); use 'NONE' to record 'no match' instead."
            )
        if not (1 <= idx <= len(candidates)):
            raise ValueError(
                f"chosen_orcid={chosen!r} for {key!r} is out of range; "
                f"only {len(candidates)} candidate(s) in the list (valid: 1-{len(candidates)})."
            )
        validated = clean_orcid(candidates[idx - 1])
        if validated is None:
            raise ValueError(
                f"candidate index {chosen!r} for {key!r} resolved to "
                f"{candidates[idx - 1]!r}, which is not a valid ORCID."
            )
        return validated
    validated = clean_orcid(chosen)
    if validated is None:
        raise ValueError(
            f"invalid chosen_orcid={chosen!r} for name_key={key!r}; must be a "
            "1-based candidate index, a full ORCID, or 'NONE'."
        )
    return validated


def apply_orcid_resolutions(
    candidates_path: Path, decisions_path: Path
) -> "pd.DataFrame":
    """Read decisions from the candidates template and append them to ``decisions_path``.

    Each ``chosen_orcid`` cell is interpreted as one of: a 1-based candidate
    index, a full ORCID, or ``NONE`` (see :func:`_resolve_chosen`). Rows with an
    empty ``chosen_orcid`` are left untouched in the template and reported as
    "unresolved" — re-running the prepare cell will regenerate the template
    while preserving any partially-filled-in values, so unresolved rows simply
    stay in the queue. Rows whose ``name_key`` is already present in the
    decisions file are skipped, so re-running is idempotent.

    Returns the updated decisions DataFrame.
    """
    import pandas as pd

    candidates_path = Path(candidates_path)
    decisions_path = Path(decisions_path)

    if not candidates_path.exists():
        raise FileNotFoundError(
            f"no candidates template at {candidates_path} — run "
            "prepare_orcid_resolution first."
        )

    # ``dtype=str, keep_default_na=False`` preserves values exactly as the
    # operator typed them: an index ``"1"`` stays ``"1"`` (pandas would otherwise
    # infer the column as float and surface it as ``"1.0"`` when other rows are
    # blank), and empty cells stay as empty strings rather than ``NaN``.
    template = pd.read_csv(candidates_path, dtype=str, keep_default_na=False)
    decisions = _load_decisions(decisions_path)
    existing = set(decisions["name_key"].astype(str))

    applied: list[dict] = []
    skipped_recorded: list[tuple[str, str]] = []
    unresolved: list[str] = []

    for _, row in template.iterrows():
        key = str(row.get("name_key", "")).strip()
        chosen = str(row.get("chosen_orcid", "")).strip()
        if not chosen:
            unresolved.append(key)
            continue
        if key in existing:
            skipped_recorded.append((key, "already in decisions file"))
            continue
        candidate_orcids = str(row.get("candidate_orcids", "")).strip()
        validated = _resolve_chosen(chosen, candidate_orcids, key)
        applied.append({
            "name_key": key,
            "name_seen": str(row.get("name_seen", "")).strip(),
            "chosen_orcid": validated,
            "candidate_orcids": candidate_orcids,
            "decided_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "notes": str(row.get("notes", "")).strip(),
        })

    if applied:
        decisions = pd.concat([decisions, pd.DataFrame(applied)], ignore_index=True)
        _save_decisions(decisions, decisions_path)

    print(
        f"applied {len(applied)} new decision(s); "
        f"{len(unresolved)} row(s) left unresolved (blank `chosen_orcid` — "
        f"kept in {candidates_path.name}); "
        f"{len(skipped_recorded)} row(s) already in the decisions file; "
        f"decisions file now has {len(decisions)} total row(s)."
    )
    for k, reason in skipped_recorded[:5]:
        print(f"  already-recorded: {k!r}  ({reason})")
    if unresolved:
        preview = ", ".join(repr(k) for k in unresolved[:5])
        more = f", ... +{len(unresolved) - 5}" if len(unresolved) > 5 else ""
        print(f"  unresolved (sample): {preview}{more}")
    return decisions
