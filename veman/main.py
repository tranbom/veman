"""
veman - virtual environment manager

Copyright (C) 2022 Mikael Tranbom

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import argparse
import os
import subprocess
import sys
import types
import venv
from pathlib import Path
from shutil import rmtree
from typing import Optional, List

from veman import __version__

DEFAULT_ENV_DIR = str(Path.home().joinpath('.veman', 'env')) + '/'
VEMAN_ENV_DIR = os.getenv('VEMAN_ENV_DIR')

ENV_DIR = VEMAN_ENV_DIR or DEFAULT_ENV_DIR


class Veman:
    """Virtual environment manager"""
    name: str
    context: types.SimpleNamespace
    environment: venv.EnvBuilder
    base_path: str
    overwrite: bool
    prompt: Optional[str]
    system_site_packages: bool
    upgrade_deps: bool
    upgrade_python: bool
    veman_activate: str
    veman_history: str
    with_pip: bool

    def __init__(
        self, name: str,
        context: types.SimpleNamespace,
        prompt: Optional[str] = None,
        system_site_packages: bool = False,
        upgrade_deps: bool = False,
        upgrade_python: bool = False,
        with_pip: bool = True,
    ):
        self.name = name
        self.context = context
        self.base_path = context.env_dir
        self.prompt = prompt
        self.system_site_packages = system_site_packages
        self.upgrade_deps = upgrade_deps
        self.upgrade_python = upgrade_python
        self.with_pip = with_pip

        # These are the default values when running python -m venv, ok to use for now
        self.environment = venv.EnvBuilder(
            clear=False,
            prompt=self.prompt,
            symlinks=True,
            system_site_packages=self.system_site_packages,
            upgrade=self.upgrade_python,
            upgrade_deps=self.upgrade_deps,
            with_pip=self.with_pip
        )
        self.overwrite = False
        self.veman_activate = self.base_path + self.name + '/bin/veman_activate'
        self.veman_history = self.base_path + self.name + '/.veman_history'

    def activate(self):
        """
        Activate an existing venv
        """
        if self.exists:
            # is_managed_venv (called as part of self.exists) contains
            # a check to verify the existence of self.veman_activate
            subprocess.run(['bash', '--rcfile', self.veman_activate], check=True)

            self.on_deactivate()
        else:
            raise ValueError(f"{self.base_path + self.name} is not a managed venv")

    def create(self, overwrite=False) -> bool:
        """
        Create a new venv
        """
        if self.exists:
            print(f"venv with name {self.name} already exists")

            self.overwrite = overwrite

            overwrite = (
                self.overwrite or
                input("Do you want to overwrite existing venv? [y/N] ").upper() == 'Y'
            )

            if not overwrite:
                return False

            self.delete()

        print(f"Creating new venv: {self.name} in {self.base_path + self.name}")
        self.environment.create(self.base_path + self.name)

        self.install_scripts()
        self.post_create()

        return True

    def shell_history(self, verbose: bool = False) -> List[str]:
        """
        Read shell history from .veman_history for venv and return a list
        with complete history
        """
        try:
            with open(self.veman_history, 'r', encoding='UTF-8') as file:
                lines = file.readlines()
        except FileNotFoundError:
            return []
        except IOError:
            print(f"Error reading {self.veman_history}")

        history = []

        for index, line in enumerate(lines, start=1):
            line = line.replace('\n', '')

            if verbose:
                line = f"[{self.name}:{index}] {line}"

            history.append(line)

        return history

    def install_scripts(self):
        """
        Install scripts into a created environment
        """
        script = generate_veman_activate_script(self)

        try:
            with open(self.veman_activate, 'w', encoding='UTF-8') as file:
                for line in script:
                    file.write(f'{line}\n')
        except IOError:
            print("Error writing veman_activate script to venv")

    def on_deactivate(self):
        """
        Things to do after deactivating a venv
        """

    def post_create(self):
        """
        Things to do after creating a new venv
        """

    @property
    def exists(self):
        """
        Return True if venv exists
        """
        return self.name in get_environments(self.context)

    def delete(self):
        """
        Delete environment
        """
        if not self.exists:
            print(f"Environment {self.name} not found")
            sys.exit(1)

        venv_path = self.base_path + self.name

        if Path(venv_path).is_dir():
            print(f"Deleting {venv_path}")
            rmtree(venv_path)

    def upgrade(self):
        """
        Upgrade core dependencies and/or python version in venv
        """
        if not self.exists:
            print(f"Environment {self.name} not found")
            sys.exit(1)

        if not self.upgrade_deps and not self.upgrade_python:
            print("Neither core dependencies or python version is set to be upgraded")
            sys.exit(1)

        if self.upgrade_deps:
            print(
                "Core dependencies (pip & setuptools) "
                "will be upgraded if not already latest"
            )

        if self.upgrade_python:
            print(
                "Python will be upgraded to this python "
                "(the python binary running the script)"
            )

            # The venv module will not replace existing symlinks so let's
            # remove them prior to upgrading the environment
            python_link = Path(self.base_path + self.name + '/bin/python')
            python3_link = Path(self.base_path + self.name + '/bin/python3')

            if python_link.is_symlink():
                print('Removing symlink', python_link)
                python_link.unlink(missing_ok=True)

            if python3_link.is_symlink():
                print('Removing symlink', python3_link)
                python3_link.unlink(missing_ok=True)

            print("Upgrading Python")

        self.environment.create(self.base_path + self.name)

    @property
    def veman_activate_script_version(self):
        """ Return version of the veman_activate script """
        return read_veman_activate_script_version(self.veman_activate)


def activate_venv(env: Veman, context: types.SimpleNamespace):
    """
    Activate virtual environment
    """
    if context.virtual_env:
        print(f"Deactivate {context.virtual_env} before activating another environment")
        sys.exit(1)

    try:
        env.activate()
    except ValueError as error:
        print(error)


def check_context(context: types.SimpleNamespace) -> bool:
    """
    Check current context
    """
    if not os.path.isabs(context.env_dir):
        print(
            f"'{context.env_dir}'",
            "does not look like a valid path. "
            "Make sure VEMAN_ENV_DIR is set to a valid absolute path."
        )
        return False

    if not context.env_dir[-1] == '/':
        context.env_dir = context.env_dir + '/'

    if not Path(context.env_dir).is_dir():
        try:
            Path(context.env_dir).mkdir(parents=True, exist_ok=True)
        except PermissionError:
            print(f"Permission denied when trying to create {context.env_dir}")
            return False

    if context.python_version < (3, 9):
        print("Python 3.9 or higher required")
        return False

    if context.os not in ('darwin', 'linux') and not context.os.startswith('freebsd'):
        print(f"Support for {context.os} not yet implemented")
        return False

    if not context.shell.endswith('/bash'):
        if context.shell == 'unknown':
            print("Could not determine shell")
        else:
            print(f"Support for {context.shell} not yet implemented")
        return False

    return True


def create_venv(
    env: Veman,
    context: types.SimpleNamespace,
    overwrite: bool,
    activate: bool
):
    """
    Create virtual environment
    """
    if context.virtual_env:
        print(f"Deactivate {context.virtual_env} before creating a new environment")
        sys.exit(1)

    created = env.create(overwrite=overwrite)

    if created and activate:
        activate_venv(env, context)


def delete_venv(
    env: Veman
) -> None:
    """ Delete virtual environment """
    if env.name:
        env.delete()
    else:
        print("No venv_name supplied")


def generate_veman_activate_script(env: Veman) -> List[str]:
    """ Generate the veman_activate script for `env`"""
    # Generating the veman_activate script inline is fine for now
    script_version = '0.2'
    etc_profile = ''

    if env.context.os == 'darwin':
        etc_profile = '/etc/profile'
        home_rc = str(Path.home()) + '/.bash_profile'
    else:
        home_rc = str(Path.home()) + '/.bashrc'

    venv_activate = env.base_path + env.name + '/bin/activate'

    lines = []

    lines.append('#!/bin/bash')
    lines.append(f'# script_version = {script_version}')
    lines.append('')
    if env.context.os == 'darwin':
        lines.append('export SHELL_SESSION_HISTORY=0')
        lines.append(f'export HISTFILE={env.veman_history}')
        lines.append(f'source {etc_profile}')
        lines.append('')
    lines.append(f'[ -r {home_rc} ] && source {home_rc}')
    lines.append(f'source {venv_activate}')
    lines.append('alias deactivate="deactivate && exit"')
    lines.append('')
    if env.context.os == 'linux' or env.context.os.startswith('freebsd'):
        lines.append(f'export HISTFILE={env.veman_history}')
        lines.append('')

    return lines


def get_context() -> types.SimpleNamespace:
    """
    Return context
    """
    context = types.SimpleNamespace()
    context.os = sys.platform
    context.python_version = sys.version_info
    context.shell = os.getenv('SHELL', 'unknown')
    context.virtual_env = None
    context.env_dir = ENV_DIR

    try:
        context.virtual_env = os.environ['VIRTUAL_ENV']
    except KeyError:
        pass

    return context


def get_environments(context: types.SimpleNamespace) -> List:
    """
    Get a list of created environments in context.env_dir
    """
    env_dir_contents = os.listdir(context.env_dir)
    environments = []

    for entry in env_dir_contents:
        if is_managed_venv(context.env_dir + entry):
            environments.append(entry)

    if environments:
        environments.sort()

    return environments


def get_temp_venv_name(context: types.SimpleNamespace) -> str:
    """Get name to use for temporary venv"""
    # 5000 should be plenty
    for num in range(0, 5000):
        venv_name = f'veman-temp{str(num)}'
        if venv_name not in get_environments(context):
            break

    return venv_name


def get_venv_name_from_user(command: str, context: types.SimpleNamespace) -> str:
    """
    List available venvs and prompt user to choose venv (or quit)
    """
    print(f"-> Select venv to {command}")

    environments = get_environments(context)
    for n_env, env in enumerate(environments, start=1):
        print(f' {n_env}) {env}')

    choice = '-1'
    while not 1 <= int(choice) <= len(environments):
        choice = input(f'(1-{len(environments)} or q): ')

        if choice == 'q':
            sys.exit(0)

    venv_name = environments[int(choice)-1]
    return venv_name


def venv_shell_history(
    context: types.SimpleNamespace,
    venv_name: Optional[str] = None,
    verbose: bool = False
) -> List[str]:
    """
    Read and return shell history for environment with name `venv_name` or
    combined history for all environments if `venv_name` is empty.
    """
    history = []

    if venv_name:
        env = Veman(name=venv_name, context=context)
        history = env.shell_history(verbose=verbose)
    else:
        for environment in get_environments(context):
            env = Veman(name=environment, context=context)
            history.extend(env.shell_history(verbose=verbose))

    return history


def print_venv_shell_history(
    context: types.SimpleNamespace,
    venv_name: Optional[str] = None,
    verbose: bool = False
):
    """
    Print shell history for environment with name `venv_name` or combined
    history for all environments if `venv_name` is empty.
    """
    history = venv_shell_history(context, venv_name, verbose)

    for entry in history:
        print(entry)


def is_managed_venv(directory: str) -> bool:
    """
    Check if given `directory` is a virtual environment managed by veman
    """
    if directory[-1] != '/':
        directory = directory + '/'

    # if the directory is a venv and contains veman_activate we will
    # assume it is managed
    directory_is_managed = (
        is_venv(directory) and
        Path(directory + 'bin/veman_activate').is_file()
    )

    return directory_is_managed


def is_venv(directory: str) -> bool:
    """
    Check if given `directory` is a virtual environment
    """
    if directory[-1] != '/':
        directory = directory + '/'

    # if the directory actually is a directory and
    # contains the following we will assume it is a venv
    directory_is_venv = (
        Path(directory).is_dir() and
        Path(directory + 'pyvenv.cfg').is_file() and
        Path(directory + 'bin').is_dir() and
        Path(directory + 'bin/python').is_file() and
        Path(directory + 'bin/activate').is_file()
    )

    return directory_is_venv


def parse_command(context: types.SimpleNamespace, options: types.SimpleNamespace):
    """
    Parse command given as argument to veman and execute appropriate functions
    """
    venv_name = ''
    upgrade_deps = False
    upgrade_python = False
    upgrade_scripts = False
    try:
        upgrade_all_venvs = options.upgrade_all_venvs
    except AttributeError:
        upgrade_all_venvs = False

    if options.command == 'create' or (
        options.command == 'history' and not options.all_history
    ):
        venv_name = options.venv_name or input("Enter name for the venv: ")

    if options.command == 'temp':
        venv_name = get_temp_venv_name(context)

    if options.command in ('activate', 'create', 'delete', 'temp', 'upgrade'):
        # upgrade_all_venvs only relevant for command upgrade
        if not upgrade_all_venvs:
            venv_name = (
                venv_name
                or options.venv_name
                or get_venv_name_from_user(options.command, context)
            )

        if options.command == 'upgrade':
            # if no component is specified, all components will be upgraded
            if not any(
                [
                    options.upgrade_deps,
                    options.upgrade_python,
                    options.upgrade_scripts,
                ]
            ):
                upgrade_deps = True
                upgrade_python = True
                upgrade_scripts = True
            else:
                upgrade_deps = options.upgrade_deps
                upgrade_python = options.upgrade_python
                upgrade_scripts = options.upgrade_scripts

        env = Veman(
            name=venv_name,
            context=context,
            prompt=options.prompt,
            system_site_packages=options.sys_site_pkgs,
            upgrade_deps=upgrade_deps,
            upgrade_python=upgrade_python,
            with_pip=options.with_pip,
        )

    if options.command == 'activate':
        activate_venv(env, context)

    elif options.command == 'create':
        create_venv(
            env,
            context,
            options.overwrite,
            options.activate
        )

    elif options.command == 'delete':
        delete_venv(env)

    elif options.command == 'history':
        print_venv_shell_history(context, venv_name, options.verbose_history)

    elif options.command == 'list':
        environments = get_environments(context)
        for env in environments:
            print(env)

    elif options.command == 'temp':
        create_venv(env, context, True, True)
        env.delete()

    elif options.command == 'upgrade':
        if upgrade_all_venvs:
            del env
            upgrade_venvs(
                context,
                options,
                upgrade_deps,
                upgrade_python,
                upgrade_scripts
            )
        else:
            upgrade_venv(env, upgrade_deps, upgrade_python, upgrade_scripts)

    else:
        print("Invalid command")


def read_veman_activate_script_version(script_path: str) -> str | None:
    """ Read version of veman_activate script from `script_path` """
    try:
        with open(script_path, 'r', encoding='UTF-8') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"Could not find file {script_path}")
        return None
    except IOError:
        print(f"Error reading {script_path}")
        return None

    # script_version was not present in the first releases of veman
    if lines[1] == '\n':
        return '0.1'

    try:
        version = lines[1].split('=')[1].strip()
    except IndexError:
        version = None
        print(
            f"Could not determine version for the veman_activate script: {script_path}"
        )

    return version or None


def upgrade_venv(
    environment: Veman,
    upgrade_deps: bool,
    upgrade_python: bool,
    upgrade_scripts: bool
) -> None:
    """ Upgrade single venv `environment` """
    if upgrade_deps or upgrade_python:
        environment.upgrade()

    if upgrade_scripts:
        print("Upgrading veman scripts")
        environment.install_scripts()


def upgrade_venvs(
    context: types.SimpleNamespace,
    options: types.SimpleNamespace,
    upgrade_deps: bool,
    upgrade_python: bool,
    upgrade_scripts: bool
) -> None:
    """ Upgrade all managed venvs """
    print("Upgrading all environments")
    print()

    environments = get_environments(context)
    for managed_env in environments:
        env = Veman(
            name=managed_env,
            context=context,
            prompt=options.prompt,
            system_site_packages=options.sys_site_pkgs,
            upgrade_deps=upgrade_deps,
            upgrade_python=upgrade_python,
            with_pip=options.with_pip,
        )

        print(f"Upgrading {managed_env}")
        upgrade_venv(env, upgrade_deps, upgrade_python, upgrade_scripts)
        del env
        print()


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Virtual Environment Manager')
    parser.add_argument(
        '--context',
        action='store_true',
        dest='context',
        help='print system environment context (mainly used for debugging & testing)'
    )
    parser.add_argument(
        '--version',
        action='store_true',
        dest='version',
        help='print veman version'
    )
    subparsers = parser.add_subparsers(dest='command')

    parser_create = subparsers.add_parser('create', help='create a new venv')
    parser_create.add_argument(
        'venv_name',
        type=str,
        nargs='?',
        help='venv name'
    )
    parser_create.add_argument(
        '--activate',
        '-a',
        action='store_true',
        default=False,
        dest='activate',
        help='activate venv after creation'
    )
    parser_create.add_argument(
        '--overwrite',
        action='store_true',
        default=False,
        dest='overwrite',
        help='overwrite venv if venv with the same name already exists'
    )
    parser_create.add_argument(
        '--prompt',
        type=str,
        help='set shell prompt prefix'
    )
    parser_create.add_argument(
        '--system-site-packages',
        action='store_true',
        default=False,
        dest='sys_site_pkgs',
        help='enable access to the system site-packages in the virtual environment'
    )
    parser_create.add_argument(
        '--without-pip',
        action='store_false',
        default=True,
        dest='with_pip',
        help='do not install pip in the virtual environment'
    )

    parser_activate = subparsers.add_parser('activate', help='activate venv')
    parser_activate.add_argument('venv_name', type=str, nargs='?', help='venv name')

    parser_delete = subparsers.add_parser('delete', help='delete an existing venv')
    parser_delete.add_argument('venv_name', type=str, nargs='?', help='venv name')

    parser_history = subparsers.add_parser(
        'history',
        help='print shell history for venv'
    )
    parser_history.add_argument('venv_name', type=str, nargs='?', help='venv_name')
    parser_history.add_argument(
        '-a',
        '--all',
        action='store_true',
        dest='all_history',
        help='print shell history for all virtual environments'
    )
    parser_history.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        dest='verbose_history',
        help='include more details when printing shell history'
    )

    # pylint: disable=unused-variable
    parser_list = subparsers.add_parser(  # noqa: F841
        'list',
        help='list virtual environments'
    )

    parser_temp = subparsers.add_parser(
        'temp',
        help='create temporary environment (deleted on deactivation)'
    )
    parser_temp.add_argument(
        '--system-site-packages',
        action='store_true',
        default=False,
        dest='sys_site_pkgs',
        help='enable access to the system site-packages in the virtual environment'
    )
    parser_temp.add_argument(
        '--without-pip',
        action='store_false',
        default=True,
        dest='with_pip',
        help='do not install pip in the temporary virtual environment'
    )

    parser_upgrade = subparsers.add_parser('upgrade', help='upgrade venv')
    parser_upgrade.add_argument('venv_name', type=str, nargs='?', help='venv name')
    parser_upgrade.add_argument(
        '--all',
        '-a',
        action='store_true',
        dest='upgrade_all_venvs',
        help='upgrade all venvs managed by veman'
    )
    parser_upgrade.add_argument(
        '--deps',
        action='store_true',
        dest='upgrade_deps',
        help='upgrade core dependencies (setuptools and pip)'
    )
    parser_upgrade.add_argument(
        '--python',
        action='store_true',
        dest='upgrade_python',
        help='upgrade python in venv to this python'
    )
    parser_upgrade.add_argument(
        '--scripts',
        action='store_true',
        dest='upgrade_scripts',
        help='upgrade veman scripts to latest version'
    )

    options = parser.parse_args()

    if options.context:
        print(get_context())
        sys.exit(0)

    if options.version:
        print(f"veman {__version__}")
        sys.exit(0)

    if not options.command:
        # print_usage is more compact and helpful than printing full help
        parser.print_usage()
        sys.exit(1)

    # set prompt, with_pip & sys_site_pkgs to default values for commands other
    # than create & temp, there is probably some cleaner way to do this.
    # argparse implementation will be reviewed when more planned commands
    # and flags have been implemented.
    if not hasattr(options, 'prompt'):
        options.prompt = None

    if not hasattr(options, 'sys_site_pkgs'):
        options.sys_site_pkgs = False

    if not hasattr(options, 'with_pip'):
        options.with_pip = True

    context = get_context()

    if not check_context(context):
        sys.exit(1)

    parse_command(context, options)
