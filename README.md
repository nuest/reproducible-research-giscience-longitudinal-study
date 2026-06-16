# Reproducible research in GIScience - longitudinal study

[![EarthArXiv Preprint](https://img.shields.io/badge/EarthArXiv%20Preprint-10.31223/X5RJ3W-FC7E2A)](https://doi.org/10.31223/X5RJ3W)

<!--TODO: Linked badge to journal paper-->

[![Zenodo deposit](https://zenodo.org/badge/DOI/10.5281/zenodo.20699084.svg)](https://doi.org/10.5281/zenodo.20699084)
[![Software Heritage deposit](https://img.shields.io/badge/Software%20Heritage-swh:1:rev:ec0bd7a2c0b60e290b6183d3e073d992d901b827-e20026?labelColor=737373)](https://archive.softwareheritage.org/swh:1:rev:ec0bd7a2c0b60e290b6183d3e073d992d901b827)

## About

This is the data and software repo to support the computational analysis related to the paper *Improving reproducibility of GIScience publications through
novel reproducibility guidelines and revised review procedures*.
This study was coordinated by Frank Ostermann <a href="https://orcid.org/0000-0002-9317-8291"><img alt="ORCID logo" src="https://info.orcid.org/wp-content/uploads/2019/11/orcid_16x16.png" width="16" height="16"/></a>,
Daniel Nüst <a href="https://orcid.org/0000-0002-0024-5046"><img alt="ORCID logo" src="https://info.orcid.org/wp-content/uploads/2019/11/orcid_16x16.png" width="16" height="16"/></a>, and
Carlos Granell <a href="https://orcid.org/0000-0003-1004-9695"><img alt="ORCID logo" src="https://info.orcid.org/wp-content/uploads/2019/11/orcid_16x16.png" width="16" height="16"/></a>, with several contributors.
See the paper for all co-authors and the paper section "Authorship contributions" for detailed contribution statements.

## Study goals and overall methodology

This study investigates the effect of revised author guidelines and reproducibility reviews on the potential reproducibility of articles published in two conference's proceedings in the area of GIScience over the past decade.
The work systematically compares AGILE conference series findings against the GIScience conference series.
The latter acts as a control group that has not undergone similar changes to its author guidelines or review process.
The results show that reproducibility guidelines and an updated review process measurably improved the potential reproducibility of AGILE publications.
The study thereby demonstrates the value of institutional and community policies in fostering reproducible research in GIScience and identifies pathways for ongoing improvement.

## Contents

### Files and folders

- `data`: raw assessment CSVs from the Google-Sheet exports, plus intermediate / aggregate artefacts produced by the analysis notebooks (e.g. derived authorship tables and the cached OpenAlex responses).
- `data-clean`: the curated, authoritative tables used as inputs to the analysis — `all-data.csv` (paper-level reproducibility assessments) and `authors.csv` (per-author-per-paper enriched view from `07_authorship.ipynb`). A `README` file documents the schema of both.
- `figs`: contains generated figures from notebooks.
- `*.qmd` files: [Quarto](https://quarto.org/) documents for data preparation and analysis.
- `*.ipynb` files: [Jupyter notebooks](https://jupyter.org/) for data analysis.
- `authorship_utils.py`: helper functions used by `07_authorship.ipynb` (DOI extraction, OpenAlex fetching with on-disk caching, author/identity resolution).
- `install.R`: R libraries used by Quarto documents.
- `requirements.txt`: Python dependencies for the Jupyter notebooks.
- `Dockerfile` & `compose.yml`: contains a Dockerfile to build a Docker image using [Docker Compose](https://docs.docker.com/compose/).
- `manuscript`: contains the manuscript LaTeX source files.

### Supplementary authorship analysis

`07_authorship.ipynb` enriches the corpus with authorship metadata from
[OpenAlex](https://openalex.org/) (via the [`pyalex`](https://pypi.org/project/pyalex/)
library), reconciles authors by ORCID with a normalised-name fallback, and reports the
overlap of authors between the AGILE and GIScience conference series over the whole corpus.
For the few DOIs not indexed by OpenAlex (notably Dagstuhl LIPIcs entries) the notebook
falls back to schema.org JSON-LD scraped from the publisher's landing page. Raw JSON
responses are cached on disk under `data/authorship-cache/` (git-ignored) so the analysis is
reproducible offline after a first run. The notebook writes the authoritative
`data-clean/authors.csv` table (one row per author-paper with resolved identities).

The `authors` branch contains extended temporal analyses building on this notebook —
year-by-year same-year overlap, reproducibility trends for cross-conference-author papers,
and a cross-group non-independence check. It is a starting point for more detailed
authorship analysis.

## Generative AI statement

`04_results_hypotheses.ipynb`, `07_authorship.ipynb`, and `authorship_utils.py` were created with the assistance of an AI coding assistant (Anthropic Claude, via Claude Code) and reviewed by the repository maintainers.

## Reproducibility

### Reproducibility setup

A **containerised environment** is based on `rocker/binder:4.4`, see `Dockerfile`, with `install.R` for dependencies of Quarto notebooks and `requirements.txt` for Jupyter notebooks.
The Docker image provides both JupyterLab and RStudio Server.

```bash
docker compose up
```

Open JupyterLab at <http://localhost:8888> (token printed to the console).
RStudio Server is available at <http://localhost:8787> (user: `rstudio`, password: `q`) or as a tab inside Jupyter Lab via the launcher/start page.

You may also run the files in a **local environment**:

For the Quarto (`.qmd`) notebooks, use a local RStudio Desktop or R installation, using `install.R` for dependencies, to render the notebooks.

For the Jupyter (`.ipynb`) notebooks, using [uv](https://docs.astral.sh/uv/):

```bash
uv venv .venv --python 3.10
source .venv/bin/activate
uv pip install -r requirements.txt
jupyter lab
```

Open `04_results_hypotheses.ipynb` and `07_authorship.ipynb` and run all cells.

You can also try to reproduce **online with Binder**, though the complex container configuration leads to failing builds regularly.

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/nuest/reproducible-research-giscience-longitudinal-study/HEAD)

### Mapping of code to figures and tables in the paper

The following scripts and notebooks each generate figures or tables in the published paper:

- `02_methods.qmd` generates **Table 1**.
- `03_results_reprolevels.qmd` generates **Figure 1**, **Figure 3**, and **Table 5**.
- `04_results_hypotheses.ipynb`generates **Table 3** and **Table 4**.
- `05_results_assessprocess.qmd` generates **Table 6** and **Table 7**.
- `06_discussion.qmd` generates **Figure 2**.
- `07_authorship.ipynb` generates the supplementary authorship-overlap figures and tables (not part of the main paper tables/figures).

## Licenses

The **code** in this repository (notebooks, scripts) is licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0). See the [LICENSE](LICENSE) file for details.
The **data** in this repository (/data, /data-clean) is licensed under [Create Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/) (CC BY 4.0). See the [LICENSE-DATA](LICENSE-DATA) file for details.
The **text** and **figures** in this repository (/manuscript, /figs) are licensed under [Create Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/) (CC BY 4.0). See the [LICENSE-MANUSCRIPT](LICENSE-DATA) file for details.

<!--
Internal links:

- https://drive.google.com/drive/folders/1pD0fJ6-vOpRJpmLScFuw2QVAg8mVt7e5
- https://www.overleaf.com/project/67407016f251c6e9fb1c3143

-->
