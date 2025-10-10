# reproducible-research-giscience-longitudinal-study


[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XYZ.svg)](https://doi.org/10.5281/zenodo.XYZ)

This is the data and software repo to support the computational analysis related to the paper *Impact of reproducible paper
guidelines on computational papers: A longitudinal study on the AGILE and GIScience conference series*. 
This study was coordinated by Frank Ostermann <a href="https://orcid.org/0000-0002-9317-8291)"><img alt="ORCID logo" src="https://info.orcid.org/wp-content/uploads/2019/11/orcid_16x16.png" width="16" height="16"/></a>,
Daniel Nüst <a href="https://orcid.org/0000-0002-0024-5046"><img alt="ORCID logo" src="https://info.orcid.org/wp-content/uploads/2019/11/orcid_16x16.png" width="16" height="16"/></a>, and 
Carlos Granell <a href="https://orcid.org/0000-0003-1004-9695"><img alt="ORCID logo" src="https://info.orcid.org/wp-content/uploads/2019/11/orcid_16x16.png" width="16" height="16"/></a>.


## Study goals and methodology


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
Several options to setup a computational environment to reproduce the analyses are offered: online and locally.


#### Reproduce online with Binder
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/nuest/reproducible-research-giscience-longitudinal-study/HEAD)

> [!NOTE]
> Building the computing enviroment in Binder can be slow.


### Reproduce 

## License

