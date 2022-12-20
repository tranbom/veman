## Changelog

### v0.1.0
- New command `upgrade` to upgrade core dependencies, python version and veman scripts in venv
- New option `--verbose` for `history` command
- Check for compatible Python version
- Documentation now available at https://tranbom.io/veman/


### v0.0.4
- New argument `-a` or `--activate` for the create command to activate a venv after creation `veman create -a testenv`
- New command `history` to print the bash history for a venv, or for all venvs with `--all`
- `veman temp` can now create multiple temporary environments simultaneously
- veman now sources `/etc/profile` and `~/.bash_profile` on macOS
- Customisations to the veman_activate bash script for macOS


### v0.0.3
- veman now maintains separate bash history for each venv, the history is automatically restored when a virtual environment is activated.


### v0.0.2
- `veman temp` will create a temporary venv which will be deleted immediately on deactivation.
- `veman --version` will print current version.


### v0.0.1
- Command `create` no longer works inside an activated virtual environment.
- Activated support for macOS with Bash (limitation: veman currently only sources ~/.bashrc)


### v0.0.1a1
- Commands `create`, `activate`, `list` & `delete` implemented
