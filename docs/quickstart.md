# Quickstart

To quickly get started with veman, follow the instructions below.
For full list of commands, see the [commands](commands.md) section.

## Installation
Install via pipx:
`pipx install veman`

Using pipx is the preferred method to install veman.

Installing with pip is not supported when the Python environment is externally managed
(for example in Debian 12), see PEP-668 for more information.

The default installation directory used by pipx is `~/.local/bin` which needs to be in your PATH.
Update the PATH manually or run `pipx ensurepath`.


## Usage
### Create and activate new venv
`veman create <venv-name>`

Create and activate a venv named "djangoenv":  
`veman create -a djangoenv`

`create -a` is similar to running create followed by activate:  
`veman create djangoenv`  
`veman activate djangoenv`

### Activate venv
`veman activate <venv-name>`

### Deactivate venv
`deactivate` (inside an activated venv)

### Delete venv
`veman delete <venv-name>`

### List managed venvs
`veman list`

### Print bash history for venv
`veman history djangoenv`


