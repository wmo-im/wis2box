# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import re

project = 'wis2box'
author = 'World Meteorological Organization (WMO)'
license = 'This work is licensed under a Creative Commons Attribution 4.0 International License'  # noqa
copyright = '2021-2022, ' + author + ' ' + license

# The full version, including alpha/beta/rc tags

file_ = '../wis2box/__init__.py'
filepath = os.path.join(os.path.abspath('..'), file_)

with open(filepath) as fh:
    contents = fh.read().strip()

    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              contents, re.M)
    if version_match:
        version = version_match.group(1)
    else:
        version = 'UNKNOWN'

release = version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'nbsphinx'
]

templates_path = ['_templates']

exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

today_fmt = '%Y-%m-%d'

html_theme = 'wmo'
html_theme_path = ['_themes']
html_css_files = [
    # 'basic.css',  # included through inheritance from the basic theme
    'wmo.css',
]
html_static_path = ['_static']

html_favicon = 'https://public.wmo.int/sites/all/themes/wmo/favicon.ico'
html_logo = 'https://public.wmo.int/sites/all/themes/wmo/logo.png'

linkcheck_ignore = [
    r'http://localhost:\d+/'
]
