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

ENV_DIR = str(Path.home().joinpath('.veman', 'env')) + '/'


class Veman:
    """Virtual environment manager"""
    name: str
    context: types.SimpleNamespace
    operating_system: str
    python_version: str
    environment: venv.EnvBuilder
    base_path: str
    overwrite: bool
    upgrade_deps: bool
    upgrade_python: bool

    def __init__(
        self, name: str,
        context: types.SimpleNamespace,
        upgrade_deps: bool = False,
        upgrade_python: bool = False,
    ):
        self.name = name
        self.context = context
        self.base_path = context.env_dir
        self.upgrade_deps = upgrade_deps
        self.upgrade_python = upgrade_python

        # These are the default values when running python -m venv, ok to use for now
        self.environment = venv.EnvBuilder(
            clear=False,
            prompt=None,
            symlinks=True,
            system_site_packages=False,
            upgrade=self.upgrade_python,
            upgrade_deps=self.upgrade_deps,
            with_pip=True
        )
        self.overwrite = False

    def activate(self):
        """
        Activate an existing venv
        """
        if self.exists:
            # is_managed_venv (called as part of self.exists) contains
            # a check to verify the existence of veman_activate
            veman_activate = self.base_path + self.name + '/bin/veman_activate'

            subprocess.run(['bash', '--rcfile', veman_activate], check=True)

            self.on_deactivate()
        else:
            raise ValueError(f"{self.base_path + self.name} is not a managed venv")

    def create(self, overwrite=False):
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
                return

            self.delete()

        print(f"Creating new venv: {self.name} in {self.base_path + self.name}")
        self.environment.create(self.base_path + self.name)

        self.install_scripts()
        self.post_create()

    def shell_history(self, verbose: bool = False) -> List[str]:
        """
        Read shell history from .veman_history for venv and return a list
        with complete history
        """
        veman_history = self.base_path + self.name + '/.veman_history'

        try:
            with open(veman_history, 'r', encoding='UTF-8') as file:
                lines = file.readlines()
        except FileNotFoundError:
            return []
        except IOError:
            print(f"Error reading {veman_history}")

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
        # Generating the veman_activate script inline is fine for now
        etc_profile = ''

        if self.context.os == 'darwin':
            etc_profile = '/etc/profile'
            home_rc = str(Path.home()) + '/.bash_profile'
        else:
            home_rc = str(Path.home()) + '/.bashrc'

        venv_activate = self.base_path + self.name + '/bin/activate'
        veman_activate = self.base_path + self.name + '/bin/veman_activate'
        veman_history = self.base_path + self.name + '/.veman_history'

        lines = []

        lines.append('#!/bin/bash')
        lines.append('')
        if self.context.os == 'darwin':
            lines.append('export SHELL_SESSION_HISTORY=0')
            lines.append(f'export HISTFILE={veman_history}')
            lines.append(f'source {etc_profile}')
            lines.append('')
        lines.append(f'[ -r {home_rc} ] && source {home_rc}')
        lines.append(f'source {venv_activate}')
        lines.append('alias deactivate="deactivate && exit"')
        lines.append('')
        if self.context.os == 'linux':
            lines.append(f'export HISTFILE={veman_history}')
            lines.append('')

        try:
            with open(veman_activate, 'w', encoding='UTF-8') as file:
                for line in lines:
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

        if os.path.isdir(venv_path):
            print(f"Deleting {venv_path}")
            rmtree(venv_path)

    def upgrade(self):
        """
        Upgrade core dependencies and/or python version in venv
        """
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

        self.environment.create(self.base_path + self.name)


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
    systems = {
        'aix': 'AIX',
        'cygwin': 'Cygwin',
        'darwin': 'Mac OS',
        'linux': 'Linux',
        'win32': 'Windows',
    }

    if not os.path.isdir(context.env_dir):
        os.makedirs(context.env_dir)

    if context.python_version < (3, 9):
        print("Python 3.9 or higher required")
        return False

    if context.os not in ('darwin', 'linux'):
        print(f"Support for {systems[context.os]} not yet implemented")
        return False

    if context.shell != '/bin/bash':
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

    env.create(overwrite=overwrite)

    if activate and env.exists:
        activate_venv(env, context)


def get_context() -> types.SimpleNamespace:
    """
    Return context
    """
    context = types.SimpleNamespace()
    context.os = sys.platform
    context.python_version = sys.version_info
    context.shell = os.environ['SHELL']
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
        os.path.isfile(directory + 'bin/veman_activate')
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
        os.path.isdir(directory) and
        os.path.isfile(directory + 'pyvenv.cfg') and
        os.path.isdir(directory + 'bin') and
        os.path.isfile(directory + 'bin/python') and
        os.path.isfile(directory + 'bin/activate')
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

    if options.command == 'create' or (
        options.command == 'history' and not options.all_history
    ):
        venv_name = options.venv_name or input("Enter name for the venv: ")

    if options.command == 'temp':
        venv_name = get_temp_venv_name(context)

    if options.command in ('activate', 'create', 'delete', 'temp', 'upgrade'):
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
            upgrade_deps=upgrade_deps,
            upgrade_python=upgrade_python,
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
        if env.name:
            env.delete()
        else:
            print("No venv_name supplied")

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

        if upgrade_deps or upgrade_python:
            env.upgrade()

        if upgrade_scripts:
            print("Upgrading veman scripts")
            env.install_scripts()

    else:
        print("Invalid command")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Virtual Environment Manager')
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
        help='Activate venv after creation'
    )
    parser_create.add_argument(
        '--overwrite',
        action='store_true',
        default=False,
        dest='overwrite'
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

    # pylint: disable=unused-variable
    parser_temp = subparsers.add_parser(  # noqa: F841
        'temp',
        help='create temporary environment (deleted on deactivation)'
    )

    parser_upgrade = subparsers.add_parser('upgrade', help='upgrade venv')
    parser_upgrade.add_argument('venv_name', type=str, nargs='?', help='venv name')
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

    if options.version:
        print(f"veman {__version__}")
        sys.exit(0)

    if not options.command:
        # print_usage is more compact and helpful than printing full help
        parser.print_usage()
        sys.exit(1)

    context = get_context()

    if not check_context(context):
        sys.exit(1)

    parse_command(context, options)
