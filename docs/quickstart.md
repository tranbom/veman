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

### Using VEMAN_ENV_DIR
The environment variable `VEMAN_ENV_DIR` can be used to override the default directory veman uses for venvs.
No venvs will be moved when changing `VEMAN_ENV_DIR`. It is possible to use different directories to maintain different sets of venvs by modifying the environment variable when running veman.

Example:  
`veman create appdev` - Create a managed environment which will be stored at the default location  
`VEMAN_ENV_DIR=/home/user/custom/location/environments veman create djangoenv57` - Create a managed environment at a custom location  
`VEMAN_ENV_DIR=/home/user/custom_location/environments veman activate djangoenv57` - Activate a managed environment stored in a custom location  

Please note that in a future version of veman the default directory will be configurable in a configuration file.
