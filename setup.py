#!/usr/bin/env python3
# Copyright 2019, 2020, 2021, 2022, 2023 Matthew Egan Odendahl
# SPDX-License-Identifier: Apache-2.0
import os
import shutil
import sys

import setuptools

os.makedirs("setup", exist_ok=True)
shutil.copy("LICENSE.txt", "setup/LICENSE.txt")

with open("README.md", encoding="utf8") as f:
    long_description = f.read()

os.chdir("setup")

sys.path.insert(0, "../src")
import hissp

hissp.transpile(hissp.__package__, "macros")

setuptools.setup(
    name="hissp",
    version=hissp.VERSION,
    description="It's Python with a Lissp.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Matthew Egan Odendahl",
    author_email="gilch@users.noreply.github.com",
    license="Apache-2.0",
    url="https://github.com/gilch/hissp",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Lisp",
        "Topic :: Software Development",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Compilers",
        "Topic :: Software Development :: Interpreters",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Pre-processors",
    ],
    keywords=(
        "lisp macro metaprogramming compiler interpreter DSL AST transpiler emacs"
        " clojure scheme language minimal REPL metaprogramming macros extensible"
        " s-expressions code-generation no-dependencies quasiquote backquote"
        " syntax-quote template Hissp Lissp"
    ),
    packages=setuptools.find_packages("../src"),
    package_data={
        "": ["*.lissp"]
    },  # If any package contains *.lissp files, include them.
    package_dir={"": "../src"},
    python_requires=">=3.10",
    entry_points={"console_scripts": ["lissp=hissp.__main__:main"]},
)
# Build dist and install:
# python setup.py bdist_wheel && pip install --force-reinstall setup\dist\hissp-*.whl
