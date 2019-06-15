import setuptools

with open("README.md") as f:
    long_description = f.read()

setuptools.setup(
    name="hissp",
    version="0.1.0",
    description="It's Python with a Lissp.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Matthew Egan Odendahl",
    author_email="hissp.gilch@xoxy.net",
    license="Apache-2.0",
    url="https://github.com/gilch/hissp",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Compilers",
        "Topic :: Software Development :: Libraries",
    ],
    keywords="lisp macro metaprogramming compiler DSL AST transpiler emacs clojure scheme",
    packages=setuptools.find_packages("src"),
    package_dir={"": "src"},
    python_requires=">=3.7",
    entry_points={"console_scripts": ["hissp=hissp.__main__:repl"]},
)
