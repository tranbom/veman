# Commands

* `veman create `- Create a new venv
* `veman activate` - Activate venv
* `veman delete` - Delete managed venv
* `veman history` - Show bash history for venv
* `veman list` - List managed venvs
* `veman temp` - Create and activate a temporary environment (deleted on deactivation)
* `veman upgrade` - Upgrade venv

### veman
Options:

* `--help` - Show brief help message
* `--context` - Print system environment context (mainly used for debugging & testing)
* `--version` - Print veman version

### veman create <venv-name\>
Create a new venv. If no <venv-name\> is given, user will be prompted for a name.

Options:

* `-a, --activate` - Activate upon creation
* `--overwrite` - Overwrite if venv with same name already exists
* `--prompt <prompt>` - Set shell prompt prefix for venv (default is venv name)
* `--system-site-packages` - Enable access to system site-packages
* `--without-pip` - Do not install pip in the virtual environment

### veman activate <venv-name\>
Activate an existing venv. If no <venv-name\> is given, a list of managed envs will be shown and the user
can choose which venv to activate.

### veman delete <venv-name\>
Delete a managed venv. If no <venv-name\> is given, a list of managed envs vill be shown and the user
can choose which venv to delete.

### veman history <venv-name\>
Print bash history for a venv or for all venvs using the option `--all`

Options:

* `-a, --all` - Can be used instead of giving a venv name to show the bash history for all venvs
* `-v, --verbose` - Print more details

### veman list
List all managed environments created by veman

### veman temp
Create and activate a temporary venv. The environment will be deleted after deactivation.
Multiple temporary environments can be created simultaneously in different terminals.

Options:

* `--system-site-packages` - Enable access to system site-packages
* `--without-pip` - Do not install pip in the temporary virtual environment

### veman upgrade <venv-name\>
Upgrade an existing venv.
If no options are given the following will be upgraded:

* Core dependencies (pip + setuptools)
* Python (will be upgraded to the python version running the veman command)
* veman scripts

It is also possible to select which components to upgrade using any of the options below.

Options:

* `-a, --all` - Upgrade all venvs managed by veman
* `--deps` - Upgrade core dependencies (pip + setuptools)
* `--python` - Upgrade Python to the python version running the veman command
* `--scripts` - Upgrade veman scripts to the latest version
