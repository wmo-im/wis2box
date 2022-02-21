# wis2box Documentation

wis2box documentation is developed using the [Sphinx Python Documentation Generator](https://www.sphinx-doc.org)
using the [reStructuredText](https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html)
format.  [Jupyter](https://jupyter.org) notebooks are also used for in-depth code examples.

## Setup
To update the documentation, ensure that Sphinx, nbsphinx and Jupyter are installed on your system (hint:
run `pip install -r requirements-dev.txt` to install the dependencies).  From here, `make html` will
build the documentation, which you can serve using any standard web server.

## Jupyter
Some of the documentation is developed using Jupyter notebooks.  To edit/update the Jupyter notebooks:

```bash
jupyter notebook
# browser should appear
```

When saving Jupyter notebooks to version control, always ensure that they are fully rendered
**before** committing (from the Jupyter menu, select *Cell -> Run All*).
