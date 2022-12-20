# Quickstart

To quickly get started with veman, follow the instructions below.
For full list of commands, see the [commands](commands.md) section.

## Installation
Install from PyPi using pip:  
`pip install veman`

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


