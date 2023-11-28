# Releases

### 2023-11-28 - v0.3.0
- veman now reads the environment variable `VEMAN_ENV_DIR` which can be used to override which directory is used for managed environments.
- The symlinks `python` and `python3` in an environments bin folder were not replaced by default by the venv module when upgrading a venv, veman now delete the symlinks to ensure that new symlinks are created during an upgrade.
- New option `--all` to the command `veman upgrade` to upgrade all existing venvs. The `--all` option can be used with or without existing options to the upgrade command.
- New option `--context` to print system environment context (mainly used for debugging & testing).


### 2023-01-03 - v0.2.0
- Activated support for FreeBSD with Bash (tested on FreeBSD and GhostBSD)
- New option `--prompt <prompt-prefix>` for `create` command to set shell prompt prefix
- New option `--system-site-packages` for `create` command to enable access to system site-packages in venv
- New option `--without-pip` for `create` command to create venv without installing pip
- Minor bug fix: Running the `upgrade` command on a non-existing venv would create a new venv
- Minor bug fix: Running `create -a <venv_name>` with a venv_name that already exists and choosing not to overwrite the existing venv would activate the existing venv


### 2022-12-20 - v0.1.1
- Minor changes to fix PyPi issue
- No functional changes to veman in this release


### 2022-12-20 - v0.1.0
- New command `upgrade` to upgrade core dependencies, python version and veman scripts in venv
- New option `--verbose` for `history` command
- Check for compatible Python version
- Documentation now available at https://tranbom.io/veman/


### 2022-12-06 - v0.0.4
- New argument `-a` or `--activate` for the create command to activate a venv after creation `veman create -a testenv`
- New command `history` to print the bash history for a venv, or for all venvs with `--all`
- `veman temp` can now create multiple temporary environments simultaneously
- veman now sources `/etc/profile` and `~/.bash_profile` on macOS
- Customisations to the veman_activate bash script for macOS


### 2022-11-22 - v0.0.3
- veman now maintains separate bash history for each venv, the history is automatically restored when a virtual environment is activated.


### 2022-11-08 - v0.0.2
- `veman temp` will create a temporary venv which will be deleted immediately on deactivation.
- `veman --version` will print current version.


### 2022-11-01 - v0.0.1
- Command `create` no longer works inside an activated virtual environment.
- Activated support for macOS with Bash (limitation: veman currently only sources ~/.bashrc)


### 2022-10-25 - v0.0.1a1
- Commands `create`, `activate`, `list` & `delete` implemented
