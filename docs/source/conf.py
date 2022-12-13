# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'wis2box guide'
copyright = '2022, World Meteorological Organization (WMO)'
author = 'World Meteorological Organization (WMO)'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

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
