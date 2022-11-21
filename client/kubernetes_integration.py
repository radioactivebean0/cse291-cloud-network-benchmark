from typing import NamedTuple, Dict

import typer
from rich.prompt import Prompt


def cli_chooser(node_list):
    class NodeOption(NamedTuple):
        name: str

    id = 0
    options: Dict[NodeOption]

    for node in node_list:
        typer.echo(f"{id} | {node.metadata.name}")
        options[str(id)] = node.metadata.name
        id += 1

    client = Prompt.ask("Which node do you want to run the client side on?", )
    options.remove(client)
    server = Prompt.ask("Which node do you want to run the server side on?", )

    return client, server
