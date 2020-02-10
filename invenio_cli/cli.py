# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 CERN.
# Copyright (C) 2019 Northwestern University.
#
# Invenio-Cli is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Invenio module to ease the creation and management of applications."""

import os
from pathlib import Path

import click

from .helpers.cli_config import CLIConfig
from .helpers.commands import Commands, ContainerizedCommands, LocalCommands
from .helpers.cookiecutter_wrapper import CookiecutterWrapper
from .helpers.docker_helper import DockerHelper


@click.group()
def cli():
    """Initialize CLI context."""


@cli.command()
@click.option('--flavour', type=click.Choice(['RDM'], case_sensitive=False),
              default='RDM', required=False)
def init(flavour):
    """Initializes the application according to the chosen flavour."""
    click.secho('Initializing {flavour} application...'.format(
        flavour=flavour), fg='green')

    cookiecutter_wrapper = CookiecutterWrapper(flavour)

    try:
        click.secho("Running cookiecutter...", fg='green')
        project_dir = cookiecutter_wrapper.cookiecutter()

        click.secho("Writing invenio-cli config file...", fg='green')
        saved_replay = cookiecutter_wrapper.get_replay()
        CLIConfig.write(project_dir, flavour, saved_replay)

        click.secho("Creating logs directory...", fg='green')
        os.mkdir(Path(project_dir) / "logs")

    except Exception as e:
        click.secho(str(e), fg='red')

    finally:
        cookiecutter_wrapper.remove_config()


@cli.command()
@click.option('--pre', default=False, is_flag=True,
              help='If specified, allows the installation of alpha releases')
@click.option('--lock/--skip-lock', default=True, is_flag=True,
              help='Lock dependencies or avoid this step')
def install(pre, lock):
    """Installs the  project locally.

    Installs dependencies, creates instance directory,
    links invenio.cfg + templates, copies images and other statics and finally
    builds front-end assets.
    """
    cli_config = CLIConfig()
    commands = LocalCommands(cli_config)
    commands.install(pre=pre, lock=lock)


@cli.command()
@click.option('--force', default=False, is_flag=True,
              help='Force recreation of db tables, ES indices, queues...')
def services(force):
    """Starts DB, ES, queue and cache services and ensures they are setup.

    --force destroys and resets services
    """
    cli_config = CLIConfig()
    commands = LocalCommands(cli_config)
    commands.services(force=force)


@cli.command()
@click.option('--force', default=False, is_flag=True,
              help='Force recreation of db tables, ES indices, queues...')
@click.option('--install-js/--no-install-js', default=True, is_flag=True,
              help="(re-)Install JS dependencies, defaults to True")
def containerize(force, install_js):
    """Setup and run all containers (docker-compose.full.yml).

    Think of it as a production compilation build + running.
    """
    cli_config = CLIConfig()
    commands = ContainerizedCommands(
        cli_config,
        DockerHelper(cli_config.get_project_shortname(), local=False)
    )
    commands.containerize(force=force, install=install_js)


@cli.command()
@click.option('--local/--containers', default=True, is_flag=True,
              help='Which environment to build, it defaults to local')
def demo(local):
    """Populates instance with demo records."""
    cli_config = CLIConfig()
    commands = Commands(cli_config, local)
    commands.demo()


@cli.command()
def run():
    """Starts the local development server.

    NOTE: this only makes sense locally so no --local option
    """
    cli_config = CLIConfig()
    commands = LocalCommands(cli_config)
    commands.run()


@cli.command()
@click.option('--install-js/--no-install-js', default=False, is_flag=True,
              help='(re-)Install JS dependencies, defaults to False')
def update(install_js):
    """Updates the current application static/assets files."""
    cli_config = CLIConfig()
    commands = LocalCommands(cli_config)
    commands.update_statics_and_assets(install=install_js)


@cli.command()
@click.option('--local/--containers', default=True, is_flag=True,
              help='Which environment to build, it defaults to local')
@click.option('--verbose', default=False, is_flag=True, required=False,
              help='Verbose mode will show all logs in the console.')
def destroy(local, verbose):
    """Removes all associated resources (containers, images, volumes)."""
    click.secho('TODO: Revisit destroy command', fg='red')


@cli.command()
@click.option('--verbose', default=False, is_flag=True, required=False,
              help='Verbose mode will show all logs in the console.')
def upgrade(verbose):
    """Upgrades the current application to the specified newer version."""
    click.secho('TODO: Implement upgrade command', fg='red')
