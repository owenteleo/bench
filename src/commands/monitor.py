from src.configuration.v1 import Configuration

import click

from loguru import logger

@click.command()
@click.pass_obj
def monitor(
    ctx,
):
    """
    Run testbench monitoring.
    """
    logger.info("Monitoring the testbench.")
    logger.warning("No monitors are currently implemented.")
