# reproducible-research-giscience-longitudinal-study

<!--TODO: Linked badge to preprint-->

<!--TODO: Linked based to journal paper-->

<!--TODO: Linked badge to Assessment Protocol-->

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XYZ.svg)](https://doi.org/)

This is the data and software repo to support the computational analysis related to the paper *Impact of reproducible paper
guidelines on computational papers: A longitudinal study on the AGILE and GIScience conference series*. 
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
So far, configuration used for Quarto documents. 

## Reproducibility

### Reproducibility setup

- TODO: create one common configuration for R/Python. Now, R notebooks are based on `rocker/rstudio:4.4`, and python notebooks on conda.


#### Reproduce online with Binder
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/)

> [!NOTE]
> Building the computing enviroment in Binder can be slow.


#### Reproduce locally with Docker


## Execution sequence of scripts

- Indicate here the execution sequence of scripts 

- Indicate here which script generates each figure/table of the published paper:
  - `02_methods.qmd` generates **Table 1** and **Table 2**.
  - `03_results_reprolevels.qmd` generates...
  - `04_results_assessprocess.qmd` generates...

## License

