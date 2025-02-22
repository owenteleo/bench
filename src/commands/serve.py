from src.server import server

import click

from loguru import logger

@click.command()
@click.pass_obj
def serve(
    ctx,
):
    """
    Run the testbench server.
    """
    logger.info("Starting testbench server.")
    logger.debug(f"Host: {ctx.cfg.host}")
    logger.debug(f"Port: {ctx.cfg.port}")
    logger.trace("This is a trace message.")

    loop = ctx.loop
    try:
        loop.run_until_complete(server(ctx))
    except KeyboardInterrupt:
        logger.info("Shutting down server.")
    finally:
        loop.close()
