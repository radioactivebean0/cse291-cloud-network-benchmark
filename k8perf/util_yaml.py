import os

import typer
import yaml


def load_to_dicts(yaml_file):
    full_path = find_file_path_from_module_root(yaml_file)

    try:
        return _load_yaml_to_dicts(full_path)
    except FileNotFoundError as e:
        typer.echo(f"Could not find {full_path}")
        raise typer.Exit()


def find_file_path_from_module_root(file_name):
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(root_dir, file_name)


def _load_yaml_to_dicts(yaml_file):
    full_path = find_file_path_from_module_root(yaml_file)
    configs = []
    with open(os.path.abspath(full_path)) as f:
        yaml_file = yaml.safe_load_all(f)
        for doc in yaml_file:
            configs.append(doc)

    return configs
