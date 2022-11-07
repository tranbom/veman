"""
Main module for veman
"""
import argparse
import os
import subprocess
import sys
import types
import venv
from pathlib import Path
from shutil import rmtree
from typing import List

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

    def __init__(self, name: str, context: types.SimpleNamespace):
        self.name = name
        self.context = context
        self.base_path = context.env_dir
        # These are the default values when running python -m venv, ok to use for now
        self.environment = venv.EnvBuilder(
            clear=False,
            prompt=None,
            symlinks=True,
            system_site_packages=False,
            upgrade=False,
            upgrade_deps=False,
            with_pip=True
        )
        self.overwrite = False

    def activate(self):
        """
        Activate an existing venv
        """
        if is_managed_venv(self.base_path + self.name):
            # is_managed_venv contains a check to verify the existence of veman_activate
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

    def install_scripts(self):
        """
        Install scripts into a created environment
        """
        # Generating the veman_activate script inline is fine for now
        home_rc = str(Path.home()) + '/.bashrc'
        venv_activate = self.base_path + self.name + '/bin/activate'
        veman_activate = self.base_path + self.name + '/bin/veman_activate'

        line1 = '#!/bin/bash'
        line2 = ''
        line3 = f'source {home_rc}'
        line4 = f'source {venv_activate}'
        line5 = 'alias deactivate="deactivate && exit"'

        try:
            with open(veman_activate, 'w', encoding='UTF-8') as file:
                file.write(f'{line1}\n{line2}\n{line3}\n{line4}\n\n{line5}\n')
        except FileNotFoundError:
            print('Error writing veman_activate script to venv')

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


def activate_venv(env: Veman, context: types.SimpleNamespace):
    """
    Activate virtual environment
    """
    if context.virtual_env:
        print(f"Deactivate {context.virtual_env} before activating another environment")
        sys.exit(1)

    env.activate()


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

    if context.os not in ('darwin', 'linux'):
        print(f"Support for {systems[context.os]} not yet implemented")
        return False

    if context.shell != '/bin/bash':
        print(f"Support for {context.shell} not yet implemented")
        return False

    return True


def create_venv(env: Veman, context: types.SimpleNamespace, overwrite: bool):
    """
    Create virtual environment
    """
    if context.virtual_env:
        print(f"Deactivate {context.virtual_env} before creating a new environment")
        sys.exit(1)

    env.create(overwrite=overwrite)


def get_context() -> types.SimpleNamespace:
    """
    Return context
    """
    context = types.SimpleNamespace()
    context.os = sys.platform
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


def get_venv_name_from_user(command: str, context: types.SimpleNamespace) -> str:
    """
    List available venvs and prompt user to choose venv (or quit)
    """
    print(f"-> Select venv to {command}")

    environments = get_environments(context)
    for n_env, env in enumerate(environments, start=1):
        print(f' {n_env}) {env}')

    choice = -1
    while not 1 <= int(choice) <= len(environments):
        choice = input(f'(1-{len(environments)} or q): ')

        if choice == 'q':
            sys.exit(0)

    venv_name = environments[int(choice)-1]
    return venv_name


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

    if options.command == 'create':
        venv_name = options.venv_name or input("Enter name for the new venv: ")

    if options.command == 'temp':
        venv_name = 'veman-temp0'

    if options.command in ('activate', 'create', 'delete', 'temp'):
        venv_name = (
            venv_name
            or options.venv_name
            or get_venv_name_from_user(options.command, context)
        )

        env = Veman(name=venv_name, context=context)

    if options.command == 'activate':
        activate_venv(env, context)

    elif options.command == 'create':
        create_venv(env, context, options.overwrite)

    elif options.command == 'delete':
        if env.name:
            env.delete()
        else:
            print("No venv_name supplied")
    elif options.command == 'list':
        environments = get_environments(context)
        for env in environments:
            print(env)
    elif options.command == 'temp':
        create_venv(env, context, True)
        activate_venv(env, context)
        env.delete()
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
        '--overwrite',
        action='store_true',
        default=False,
        dest='overwrite'
    )

    parser_activate = subparsers.add_parser('activate', help='activate venv')
    parser_activate.add_argument('venv_name', type=str, nargs='?', help='venv name')
    parser_activate.add_argument('--last', action='store_true', dest='last')

    parser_delete = subparsers.add_parser('delete', help='delete an existing venv')
    parser_delete.add_argument('venv_name', type=str, nargs='?', help='venv name')

    # pylint: disable=unused-variable
    parser_list = subparsers.add_parser('list', help='list virtual environments')

    # pylint: disable=unused-variable
    parser_temp = subparsers.add_parser(
        'temp',
        help='create temporary environment (deleted on deactivation)'
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
