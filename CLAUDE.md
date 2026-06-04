# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

Data and analysis repository for the paper *Longitudinal assessment of research in GIScience domain shows a positive impact of reproducible research practices*. The analysis assesses reproducibility levels of AGILE and GIScience conference papers across multiple years.

## Environment & commands

Two parallel runtimes are used. There is currently **no single unified environment** (see README TODO).

- **R / Quarto** (`*.qmd` files): built on `rocker/rstudio:4.4`. Dependencies installed via `install.R` (`here`, `tidyverse`, `gt`, `ggthemes`, `patchwork`, `ggalluvial`).
- **Python / Jupyter** (`04_results_hypotheses.ipynb`, `07_authorship.ipynb`, `09_authorship-historic.ipynb`): conda env `agilegisc` defined in `04_environment.yml` (pandas, numpy, scipy, statsmodels, jupyterlab; plus `matplotlib`, `matplotlib-venn`, and `pyalex` via pip for notebooks 07/09).

Run the RStudio container locally:

```sh
docker compose up          # RStudio at http://localhost:8787, user: rstudio, pass: q
```

Render a single Quarto document:

```sh
quarto render 03_results_reprolevels.qmd
```

Execute the Python notebook:

```sh
conda env create -f 04_environment.yml && conda activate agilegisc
jupyter lab 04_results_hypotheses.ipynb
```

## Pipeline structure

Numeric prefixes define execution order. Outputs flow: `data/` → `data-clean/all-data.csv` → figures/tables.

1. `01_datacleaning.qmd` — reads raw Google-Sheet-exported CSVs from `data/` (the `Both Reviewers step 5 WiP ...csv` is the canonical input), produces `data-clean/all-data.csv`.
2. `02_methods.qmd` — Table 1, Table 2.
3. `03_results_reprolevels.qmd` — Figure 2, Figure 3, Table 3.
4. `04_results_hypotheses.ipynb` — Tables 4–7 (Python; the only non-R step).
5. `05_results_assessprocess.qmd` — Table 8, Figure 4, Tables 9–10.
6. `06_discussion.qmd` — Figure 5.
7. `07_authorship.ipynb` — supplementary authorship analysis (Python). Resolves a DOI per paper from the `link` column, fetches metadata from OpenAlex (cached under `data/authorship-cache/`, git-ignored), falls back to schema.org JSON-LD scraped from the publisher landing page when OpenAlex does not index the DOI, and reports corpus-wide cross-conference author overlap (Part A: Venn, counts, author table) keyed on ORCID with a normalised-name fallback. Writes the authoritative `data-clean/authors.csv`. Heavy helpers live in [authorship_utils.py](authorship_utils.py) so the notebook stays light.
8. `09_authorship-historic.ipynb` — temporal authorship analysis (Python). Reads `data-clean/authors.csv` from step 7. Covers year-by-year same-year overlap (Part B; GIScience off-years correctly yield zero), reproducibility trends for cross-conference-author papers vs. the full corpus, and a cross-group non-independence check for the four analytical groups used in step 4.

`data-clean/` holds only the two authoritative tables — `all-data.csv` and `authors.csv` (the per-author-per-paper enriched view from notebook 07). All derived / aggregate / debug artefacts (`authors-overlap.csv`, `authors-cross-conference.csv`, `authors-cross-conference-yearly.csv`, `authors-title-verification.csv`, the OpenAlex JSON cache, the optional `orcid-resolutions.csv`) live under `data/`. When extending a notebook, write the one canonical curated table to `data-clean/` and put intermediate / regenerable outputs in `data/`.

All downstream `.qmd` / `.ipynb` files read `data-clean/all-data.csv`; do not consume raw `data/` CSVs from downstream steps. Figures are written to `figs/`.

## Data model

`data-clean/all-data.csv` schema is documented in `data-clean/README.md`. Key points for analysis:

- Each row is one conference paper (AGILE or GIScience).
- Reproducibility is coded per criterion (`data`, `methods`, `results`) using levels `U` / `D` / `A` / `O` / `NA` (increasing reproducibility).
- Two independent reviewers (`rev1_*`, `rev2_*`) plus `consolidated_*` consensus columns — use `consolidated_*` for headline results; use `rev1_*` / `rev2_*` only for inter-rater / disagreement analysis.
- `disagr_type` / `disagr_id` capture reviewer-disagreement categories.
- `agile_badge` / `agile_reproreport` are AGILE-only and should be `NA` / `FALSE` for GIScience rows.

Column renames happen inside `01_datacleaning.qmd` (e.g. `REV1 CP?` → `REV1_CP`). When adding fields, update both the `dplyr::select` in `01_datacleaning.qmd` and the data sheet in `data-clean/README.md`.

## Manuscript

LaTeX sources live in `manuscript/` (`main.tex`, `references.bib`, `josis.cls` / `josis-preprint.cls`). The manuscript is authored in Overleaf; the copy here is a snapshot. Figures referenced from the manuscript are expected at `manuscript/img/` — figures generated into `figs/` are copied over manually.

## Licensing split

Code is Apache-2.0; data (`data/`, `data-clean/`) is CC-BY-4.0; manuscript text and figures (`manuscript/`, `figs/`) are CC-BY-4.0. Keep additions in the correct directory so the license statement in the README stays accurate.
