import os

import typer
import yaml


def load_to_dicts(yaml_file):
    try:
        return _load_yaml_to_dicts(yaml_file)
    except FileNotFoundError as e:
        typer.echo("error: " + str(e))
        typer.echo(f"Could not find {yaml_file}")

        typer.Exit()


def _load_yaml_to_dicts(yaml_file):
    configs = []
    with open(os.path.abspath(yaml_file)) as f:
        yaml_file = yaml.safe_load_all(f)
        for doc in yaml_file:
            configs.append(doc)

    return configs
