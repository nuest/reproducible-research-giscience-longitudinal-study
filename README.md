# reproducible-research-giscience-longitudinal-study

<!--TODO: Linked badge to preprint-->

<!--TODO: Linked badge to journal paper-->

<!--TODO: Linked badge to Assessment Protocol-->

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17733628.svg)](https://doi.org/10.5281/zenodo.17733628)

This is the data and software repo to support the computational analysis related to the paper *Longitudinal assessment of research in GIScience domain shows a positive impact of reproducible research practices*. 
This study was coordinated by Frank Ostermann <a href="https://orcid.org/0000-0002-9317-8291"><img alt="ORCID logo" src="https://info.orcid.org/wp-content/uploads/2019/11/orcid_16x16.png" width="16" height="16"/></a>,
Daniel Nüst <a href="https://orcid.org/0000-0002-0024-5046"><img alt="ORCID logo" src="https://info.orcid.org/wp-content/uploads/2019/11/orcid_16x16.png" width="16" height="16"/></a>, and 
Carlos Granell <a href="https://orcid.org/0000-0003-1004-9695"><img alt="ORCID logo" src="https://info.orcid.org/wp-content/uploads/2019/11/orcid_16x16.png" width="16" height="16"/></a>.

Acknowledgement: [AGILE](https://agile-gi.eu/)...

## Study goals and overall methodology


TODO: 

Data...

- AGILE "averages" dataset as csv from previous paper
- AGILE dataset, full papers for years ... - ...
- GIScience dataset, full papers for years xxxx, yyyy, ...
- citation data?

Methods...

- alluvial plot for both pre and post intervention AGILE
- alluvial plot for GIScience matching pre/post years
- timeline plot of actual data points and averages, wich old AGILE dataset in light colour for loose reference


## Contents

- `data`: raw assessment CSVs from the Google-Sheet exports, plus intermediate / aggregate artefacts produced by the analysis notebooks (e.g. derived authorship tables and the cached OpenAlex responses).
- `data-clean`: the curated, authoritative tables used as inputs to the analysis — `all-data.csv` (paper-level reproducibility assessments) and `authors.csv` (per-author-per-paper enriched view from `07_authorship.ipynb`). A `README` file documents the schema of both.
- `figs`: contains generated figures from notebooks.
- `*.qmd` files: [Quarto](https://quarto.org/) documents for data preparation and analysis.
- `*.ipynb` files: [Jupyter notebooks](https://jupyter.org/) for data analysis.
- `authorship_utils.py`: helper functions used by `07_authorship.ipynb` (DOI extraction, OpenAlex fetching with on-disk caching, author/identity resolution).
- `install.R`: R libraries used by Quarto documents.
- `04_environment.yml`: Python conda environment used by Jupyter notebooks.
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

Both `07_authorship.ipynb` and `authorship_utils.py` were created with the assistance of an
AI coding assistant (Anthropic Claude, via Claude Code) and reviewed by the repository
maintainers.

## Reproducibility

### Reproducibility setup

- TODO: create one common configuration for R/Python. Now, R notebooks are based on `rocker/rstudio:4.4`, and python notebooks on conda.

#### Reproduce online with Binder

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/)

> [!NOTE]
> Building the computing enviroment in Binder can be slow.

#### Reproduce locally with Docker

TODO

### Mapping of code to figures and tables in the paper

The following scripts and notebooks each generate figures or tables in the published paper:

- `02_methods.qmd` generates **Table 1** and **Table 2**.
- `03_results_reprolevels.qmd` generates **Figure 2**, **Figure 3**, and **Table 3**.
- `04_results_hypotheses.ipynb`generates **Table 4**, **Table 5**, **Table 6**, and **Table 7**.
- `05_results_assessprocess.qmd` generates **Table 8**, **Figure 4**, **Table 9**, and **Table 10**.
- `06_discussion.qmd` generates **Figure 5**.
- `07_authorship.ipynb` generates the supplementary authorship-overlap figures and tables (not part of the main paper tables/figures).

## License

The **code** in this repository (notebooks, scripts) is licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0). See the [LICENSE](LICENSE) file for details.
The **data** in this repository (/data, /data-clean) is licensed under [Create Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/) (CC BY 4.0). See the [LICENSE-DATA](LICENSE-DATA) file for details.
The **text** and **figures** in this repository (/manuscript, /figs) are licensed under [Create Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/) (CC BY 4.0). See the [LICENSE-MANUSCRIPT](LICENSE-DATA) file for details.

<!--
Internal links:

- https://drive.google.com/drive/folders/1pD0fJ6-vOpRJpmLScFuw2QVAg8mVt7e5
- https://www.overleaf.com/project/67407016f251c6e9fb1c3143

-->