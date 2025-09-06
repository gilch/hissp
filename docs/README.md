<!--
Copyright 2023, 2024 Matthew Egan Odendahl
SPDX-License-Identifier: CC-BY-SA-4.0
-->
# Hissp Documentation
This directory contains the reStructuredText source of Hissp's documentation,
along with associated configuration and helper files,
including the Lissp syntax highlighter.
A significant additional portion of Hissp's rendered documentation is derived from
docstrings in Hissp's source code (the API docs).

## Quick Links
${\boldsymbol {\color{royalblue}{(}\color{green}{\textsf -}\color{gold}{)}\color{gainsboro}{\kern-1.5pt{\textsf :}}}}$
[Rendered Documentation ](https://hissp.readthedocs.io/) 🢦 START HERE.  
<sup>|</sup>||' [Gitter Chat](https://gitter.im/hissp-lang/community)  
[**m**] [Matrix Chat](https://matrix.to/#/#hissp-lang_community:gitter.im) (same room)  
⭐ [On GitHub (Source Code)](https://github.com/gilch/hissp)  
🗪 [Discussions Page](https://github.com/gilch/hissp/discussions)  
📖 [Hissp Wiki](https://github.com/gilch/hissp/wiki)  

## Building Docs
Hissp proper has no dependencies, but its documentation is built with Sphinx.
Install documentation dependencies from this directory with
```
pip install -r requirements.txt
```
Docs are typically built with
```
make html
```
