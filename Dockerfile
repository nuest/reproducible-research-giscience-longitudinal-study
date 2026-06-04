# Based on https://rocker-project.org/images/ — rocker/binder ships R + RStudio Server
# + a Python venv at /opt/venv + JupyterLab + IRkernel + jupyter-rsession-proxy
# (RStudio is accessible as a tab inside JupyterLab via the proxy).
FROM rocker/binder:4.4

ENV HOME=/home/rstudio

USER root

# Install R packages
COPY install.R ${HOME}/install.R
RUN R --quiet -f ${HOME}/install.R

# Install Python dependencies into the venv rocker/binder provides at /opt/venv
COPY requirements.txt ${HOME}/requirements.txt
RUN /opt/venv/bin/pip install --no-cache-dir -r ${HOME}/requirements.txt

# Copy repo and fix ownership, see also .dockerignore for excluded files
COPY . ${HOME}
RUN chown -R rstudio:rstudio ${HOME}

USER rstudio
WORKDIR ${HOME}

# JupyterLab is the primary entry point; RStudio is available on port 8787 directly
# or via the RStudio launcher tile in JupyterLab.
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--no-browser"]
