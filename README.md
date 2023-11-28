# veman - Virtual Environment Manager

[![pipeline status](https://gitlab.com/tranbom/veman/badges/main/pipeline.svg)](https://gitlab.com/tranbom/veman/-/pipelines)
[![PyPi - Release](https://img.shields.io/pypi/v/veman)](https://pypi.org/project/veman/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/veman)](https://pypi.org/project/veman/)
[![PyPI - License](https://img.shields.io/pypi/l/veman?color=blue)](https://pypi.org/project/veman/)

veman is a lightweight virtual environment manager using venv.
With veman it is easier to manage multiple environments.

Note: veman is under active development and currently supports Bash in FreeBSD, Linux & macOS.

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


## Installation

Install via pipx:
`pipx install veman`

Using pipx is the preferred method to install veman.

Installing with pip is not supported when the Python environment is externally managed
(for example in Debian 12), see PEP-668 for more information.

The default installation directory used by pipx is `~/.local/bin` which needs to be in your PATH.
Update the PATH manually or run `pipx ensurepath`.

### Dependencies

- Python >=3.9
- venv

### Installation instructions for Debian 12 and distributions based on Debian 12

Install pip, pipx & venv from the Debian repository:  
`sudo apt-get update`  
`sudo apt-get install python3-pip python3-venv pipx`  

Install veman with pipx and update PATH (if necessary):  
`pipx install veman`  
`pipx ensurepath`  

## Usage

### Create a new virtual environment

`veman create` or
`veman create <environment-name>`

Use `-a` or `--activate` after the create command to automatically activate
the venv after creation.

Examples:  
`veman create djangoenv`  
`veman create -a flaskenv`  
`veman create --activate testenv1`  


### Activate a virtual environment

`veman activate` or
`veman activate <environment-name>`

Example:
`veman activate djangoenv`


### Deactivate a virtual environment

`deactivate` (inside an active venv)


### List created virtual environments

`veman list`


### Delete a virtual environment

`veman delete` or `veman delete <environment-name>`

Example: `veman delete djangoenv`


### Create and activate a temporary environment

Create a temporary environment which will be deleted immediately when
deactivating the environment.

`veman temp`

To exit & delete the temporary environment type `deactivate`

veman supports creating multiple temporary environments simultaneously.


### Bash history

veman creates a separate bash history file for each venv.

The history of bash commands executed inside an activated venv is saved
in the root folder of the venv as **.veman_history** and everytime
a virtual environment is activated the bash history will be restored.

The bash builtin `history` will print the environments history when a venv is activated and
when the virtual environment is deactivated `history` will automatically switch back to using
the regular bash history file (usually ~/.bash_history).

veman also has its own `history` command which can be used without having to activate
a venv, making it easy to find which commands have been run in different environments.

`veman history <environment-name>` will list the bash history for a single venv.

`veman history --all` will print the bash history for all venvs, which can be useful to
quickly find a command in the history across environments. Currently there is no specific order of the
venvs in which the history is printed.

The `--verbose` option will print some additional details, such as venv name and line number.


### Upgrade venv

Various components of a venv can be upgraded with veman.
Running `veman upgrade <environment-name>` will upgrade the following:

- Core dependencies (pip + setuptools)
- Python (will be upgraded to the python version running the veman command)
- veman scripts

It is also possible to select which components to upgrade using any of the following options when running `veman upgrade`:

- `--deps` - Upgrade core dependencies
- `--python` - Upgrade Python
- `--scripts` - Upgrade veman scripts

Upgrading the veman scripts can be useful when a new version of veman has been released to ensure compatibility of new
veman features in a venv created with an older version of veman.

All managed venvs can be upgraded with the option `--all`:

`veman upgrade --all`


### Full list of available commands and options

* Documentation: [https://tranbom.io/veman/](https://tranbom.io/veman/)


## Notes

veman sources `~/.bashrc` in Linux & FreeBSD. veman is mainly tested in distributions that are
derivatives of Debian which automatically sources `/etc/bash.bashrc`.

veman sources `/etc/profile` and `~/.bash_profile` in macOS.


## Planned features

- Connect a managed venv with a specific git repository (e.g., automatic cd on activate)
- User defined commands to run on activate (python and/or shell)
- Compatibility with zsh & more shells
- Command to add local paths to .pth-file in venv
- Configuration file with settings for veman (e.g., path to env directory)
- Adopt existing unmanaged venvs
- Auto-update managed venvs after veman has been upgraded


## License

GPL-3.0-only
