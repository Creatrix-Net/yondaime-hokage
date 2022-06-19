# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys


# -- Project information -----------------------------------------------------

project = "fluxpoint.py"
copyright = "2022, Dhruva Shaw"
author = "Dhruvacube"

# The full version, including alpha/beta/rc tags
version = "v2.0beta"
# The full version, including alpha/beta/rc tags.
release = version

# This assumes a tag is available for final releases
branch = "master" if version.endswith("a") else "v" + version

sys.path.insert(0, os.path.abspath(".."))
sys.path.append(os.path.abspath("extensions"))


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "builder",
    "sphinx.ext.autodoc",
    "autoapi.extension",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinxcontrib_trio",
    "details",
    "resourcelinks",
]
autoapi_dirs = autodoc_dirs = ["../minato_namikaze"]
autodoc_member_order = "bysource"
autodoc_typehints = "description"

# maybe consider this?
# napoleon_attr_annotations = False

extlinks = {
    "issue": ("https://github.com/The-4th-Hokage/yondaime-hokage/issues/%s", "GH-"),
}

# Links used for cross-referencing stuff in other documentation
intersphinx_mapping = {
    "py": ("https://docs.python.org/3", None),
    "aio": ("https://docs.aiohttp.org/en/stable/", None),
    "dis": ("https://discordpy.readthedocs.io/en/latest/", None),
    "discordutils": ("https://discordutils.readthedocs.io", None),
    "mal": ("https://mal-api.readthedocs.io/en/latest/index.html", None),
    "sql": ("https://www.sqlalchemy.org/", None),
    "together": ("https://docs.discord-together.ml/1.2/", None),
    "dagpi": ("https://asyncdagpi.readthedocs.io/en/latest/", None),
    "jishaku": ("https://jishaku.readthedocs.io/en/latest/", None),
    "cachetools": ("https://cachetools.readthedocs.io/en/stable/", None),
    "gtts": ("https://gtts.readthedocs.io/en/latest/", None),
    "pillow": ("https://pillow.readthedocs.io/en/stable/", None),
    "psutils": ("https://psutil.readthedocs.io/en/latest/", None),
    "pygit2": ("https://www.pygit2.org/", None),
    "dateutil": ("https://dateutil.readthedocs.io/en/stable/", None),
    "sentry": ("https://getsentry.github.io/sentry-python/", None),
    "uvloop": ("https://uvloop.readthedocs.io/", None),
}
# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]


# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
html_domain_indices = True


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#

html_experimental_html5_writer = True

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "basic"

suppress_warnings = ["autoapi"]


html_context = {
    "discord_invite": "https://discord.gg/vfXHwS3nmQ",
}

resource_links = {
    "discord": "https://discord.gg/vfXHwS3nmQ",
    "issues": "https://github.com/The-4th-Hokage/yondaime-hokage/issues",
    "discussions": "https://github.com/The-4th-Hokage/yondaime-hokage/discussions",
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
exclude_patterns = ["_build"]

pygments_style = "friendly"

html_search_scorer = "_static/scorer.js"
html_favicon = "./_static/logo.png"

html_js_files = ["custom.js", "settings.js", "copy.js", "sidebar.js"]

man_pages = [
    ("index", "fluxpoint.py", "fluxpoint.py Documentation", ["Dhruva Shaw"], 1)
]

# If true, show URL addresses after external links.
man_show_urls = True


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        "index",
        "fluxpoint.py",
        "fluxpoint.py Documentation",
        "Dhruvacube",
        "fluxpoint.py",
        "One line description of project.",
        "Miscellaneous",
    ),
]

# Documents to append as an appendix to all manuals.
# texinfo_appendices = []

# If false, no module index is generated.
# texinfo_domain_indices = True

# How to display URL addresses: 'footnote', 'no', or 'inline'.
# texinfo_show_urls = 'footnote'

# If true, do not generate a @detailmenu in the "Top" node's menu.
texinfo_no_detailmenu = False

source_suffix = ".rst"

# The encoding of source files.
# source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = "index"


def autodoc_skip_member_handler(app, what, name, obj, skip, options):
    return (
        "__str__" in name.lower()
        or "__init__" in name.lower()
        or "__repr__" in name.lower()
        or setup in name.lower()
    )


# Automatically called by sphinx at startup


def setup(app):
    app.connect("autodoc-skip-member", autodoc_skip_member_handler)
