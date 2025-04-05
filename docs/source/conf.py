# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import sys
import os

sys.path.append(os.path.abspath("../.."))
# sys.path.append(os.path.abspath(".."))

project = "Contacts API"
copyright = "2025, Andrii Veremii"
author = "Andrii Veremii"
release = "1.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# extensions = []
#
# templates_path = ['_templates']
# exclude_patterns = []

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",  # Підтримка Google style docstrings
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "bizstyle"  # Використовуємо вбудовану тему bizstyle
html_static_path = ["_static"]

# Додаткові налаштування HTML
html_show_sourcelink = True
html_show_sphinx = True
html_show_copyright = True

# Мова документації
language = "uk"

# Налаштування автодокументування
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
    "special-members": "__init__,metadata",
}

# Налаштування для кращого відображення docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = True
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = None

# Додаткові налаштування для кращого вигляду
html_theme_options = {"rightsidebar": False, "sidebarwidth": "300px"}

# Додаємо власні стилі CSS
html_css_files = [
    "custom.css",
]
