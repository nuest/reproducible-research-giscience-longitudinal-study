# This Dockerfile is based on https://rocker-project.org/images/
FROM rocker/rstudio:4.4

## Declares build arguments
#ARG NB_USER

## Declares ENV values
ENV USER=rstudio
ENV HOME=/home/rstudio

## Copies all repo files into the Docker Container
USER root
COPY . ${HOME}
RUN chown -R ${USER} ${HOME}

## Become normal user again
USER ${NB_USER}

# run install.R script if any
RUN echo 'Install R packages...'   
RUN R --quiet -f ${HOME}/install.R

# --- Metadata ---
