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

- `data`: contains several CSV files that contained assessment data of the eligible conference papers.
- `data-clean`: contains a processed CSV file ready for analysis and a `README` file (data sheet) to describe each column.
- `figs`: contains generated figures from notebooks.
- `*.qmd` files: [Quarto](https://quarto.org/) documents for data preparation and analysis.
- `*.ipynb` files: [Jupyter notebooks](https://jupyter.org/) for data analysis.
- `install.R`: R libraries used by Quarto documents.
- `06_environemnt.yml`: Python libraries used by Jupyter notebooks.
- `Dockerfile` & `compose.yml`: contains a Dockerfile to build a Docker image using [Docker Compose](https://docs.docker.com/compose/).
- `manuscript`: contains the manuscript LaTeX source files.

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

## License

The **code** in this repository (notebooks, scripts) is licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0). See the [LICENSE](LICENSE) file for details.
The **data** in this repository (/data, /data-clean) is licensed under [Create Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/) (CC BY 4.0). See the [LICENSE-DATA](LICENSE-DATA) file for details.
The **text** and **figures** in this repository (/manuscript, /figs) are licensed under [Create Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/) (CC BY 4.0). See the [LICENSE-MANUSCRIPT](LICENSE-DATA) file for details.

<!--
Internal links:

- https://drive.google.com/drive/folders/1pD0fJ6-vOpRJpmLScFuw2QVAg8mVt7e5
- https://www.overleaf.com/project/67407016f251c6e9fb1c3143

-->