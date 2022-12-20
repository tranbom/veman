# veman - Virtual Environment Manager

[![pipeline status](https://gitlab.com/tranbom/veman/badges/main/pipeline.svg)](https://gitlab.com/tranbom/veman/-/pipelines)
[![pypi release](https://img.shields.io/pypi/v/veman)](https://pypi.org/project/veman/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/veman)
![PyPI - License](https://img.shields.io/pypi/l/veman?color=blue)


veman is a lightweight virtual environment manager for Python using venv.
With veman it is easier to manage multiple environments.

Note: veman is under active development and currently supports Bash in Linux & macOS.

veman aims to be a simple manager for Python's venv package. The intention of veman is
to be a comprehensive companion tool for venv, facilitating the creation/activation &
management of virtual environments, with some extra features that aids development with
Python.

veman is primarily developed for Linux & macOS. veman does not yet support
Windows. Windows compatibility will most likely be implemented in a future version but it is
currently not a prioritised feature.

* GitHub: [https://github.com/tranbom/veman](https://github.com/tranbom/veman)
* GitLab: [https://gitlab.com/tranbom/veman](https://gitlab.com/tranbom/veman)
* PyPi: [https://pypi.org/project/veman](https://pypi.org/project/veman)
* Documentation: [https://tranbom.io/veman/](https://tranbom.io/veman/)


## Features

* Simple command line interface to create and manage venvs
* Bash history is maintained per venv and restored on venv activation
* Bash history can be listed for single venv or for all venvs
* Command to create temporary venv which is deleted on deactivation
* Upgrade command to upgrade venv components


## Requirements
* Python >= 3.9
* venv
* Linux or macOS with Bash

## Terminology
The words __venv__, __env__, __environment__ & __virtual environment__ are used interchangeably throughout the veman documentation.
