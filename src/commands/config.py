from src.configuration.v1 import Configuration

import click
import pathlib
import sys
import yaml

from loguru import logger

@click.group(invoke_without_command=True)
@click.option("--example", is_flag=True, help="Emits an example configuration.")
@click.option("--profile", type=click.Choice(["default", "teleo"]), default="teleo", help="The profile to use.")
@click.option("--output", "-o", default=None, help="Path to output. Default is stdout.")
@click.pass_context
def config(
    context,
    example,
    profile,
    output,
):
    """
    Manage the testbench configuration.
    """
    if context.invoked_subcommand is None:
        ctx = context.obj
        if example:
            match profile:
                case "default":
                    config = Configuration.builder().build()
                case "teleo":
                    builder = Configuration.builder()\
                        .with_host("localhost")\
                        .with_port(8080)\
                        .with_tcan("socketcan", "can0")\
                        .with_mcan("socketcan", "can1")
                    config = builder.build()
                case _:
                    logger.error(f"Unsupported profile: {profile}")
                    exit(1)
        else:
            config = ctx.cfg

        if output is not None:
            if pathlib.Path(output).exists():
                print(f"\033[1;38;5;220mwarning\033[0m: File '{output}' already exists. Overwrite? [y/N] ", end="")
                choice = input()
                if choice != "y":
                    print("Aborted.")
                    sys.exit(1)

            with open(output, "w") as f:
                data = Configuration.serialize(config, f)
        else:
            print(Configuration.serialize(config))
