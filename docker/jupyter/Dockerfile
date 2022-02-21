FROM jupyter/datascience-notebook:latest

# Inspect the Dockerfile at:
# https://github.com/jupyter/docker-stacks/tree/HEAD/datascience-notebook/Dockerfile

# install additional package...
RUN pip install --no-cache-dir OWSLib lxml
RUN mamba install --quiet --yes \
    "udunits" \
    "r-sf" \
    "r-dplyr" && \
    mamba clean --all -f -y && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"