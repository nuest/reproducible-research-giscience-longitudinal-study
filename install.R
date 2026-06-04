# R package dependencies for the Quarto notebooks.
#
# Pin to the same PPM snapshot used by rocker/rstudio:4.4 (2025-04-10).
# This ensures rocker/binder (which otherwise defaults to latest CRAN) gets
# the same package versions. The snapshot predates ggplot2 4.0 (May 2025),
# which broke ggalluvial 0.12.6 and patchwork 1.3.2 in ways not yet fixed
# on CRAN. Remove or advance the pin once both packages support ggplot2 4.x.
options(repos = c(CRAN = "https://p3m.dev/cran/__linux__/noble/2025-04-10"))

install.packages("here")
install.packages("tidyverse")
install.packages("gt")
install.packages("ggthemes")
install.packages("patchwork")
install.packages("ggalluvial")
install.packages("knitr")
install.packages("rmarkdown")
