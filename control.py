"""
file: control.py
brief: control JTECU
"""

from src.queue import Queue

from src.tcan_commands import SystemMode

import asyncio
import can
import click
import requests

from enum import Enum
from loguru import logger
from microdot import Microdot

class Context:
    def __init__(
        self,
        interface: str,
        channel: str,
        jtecu_id: int,
        host: str,
        port: int,
    ):
        self._interface = interface
        self._channel = channel
        self._jtecu_id = jtecu_id
        self._host = host
        self._port = port

        self._loop = asyncio.new_event_loop()

        self._command_queue = Queue(self._loop)

        self._teleo_mode = SystemMode.MANUAL

        self._axis_data = bytearray(8)

    @property
    def loop(self):
        return self._loop

    @property
    def interface(self):
        return self._interface

    @property
    def channel(self):
        return self._channel
    
    @property
    def jtecu_id(self):
        return self._jtecu_id

    @property
    def host(self):
        return self._host
    
    @property
    def port(self):
        return self._port
    
    @property
    def command_queue(self):
        return self._command_queue
    
    @property
    def teleo_mode(self):
        return self._teleo_mode
    
    @property
    def axis_data(self):
        return self._axis_data
    
    def set_teleo_mode(self, mode: SystemMode):
        if mode in SystemMode:
            self._teleo_mode = mode

    def set_axis_data(self, data: bytearray):
        self._axis_data = data

    def bus(self) -> can.interface.Bus:
        """
        Create a python-can Bus object using the given configuration.
        Note: this is addresses the fact that a python-can Bus object is opened
        when it is created. Use of this method allows the application to decide
        when access to the bus is needed.

        Usage:
        ```python
        with ctx.bus() as bus:
            # do something with the bus
        ```
        """
        try:
            return can.interface.Bus(
                interface=self._interface,
                channel=self._channel,
                filters=[
                    {"can_id": 0x11, "can_mask": 0x21, "extended": False},
                ],
            )
        except OSError as e:
            if e.errno == 19:
                logger.error(
                    f"No {self._interface} device '{self._channel}' found."
                )
                exit(1)
            else:
                raise e
            
            
    

# Configure a simple web server
app = Microdot()

@app.post("/enter_mode/<int:mode>")
async def enter_mode(request, mode: int):
    logger.info(f"enter_mode {mode}")
    if mode in SystemMode:
        app.context.set_teleo_mode(mode)
        return {"status": "ok"}
    else:
        return {"status": "error", "message": "Invalid mode"}

@app.post("/set_axis")
async def set_axis(request):
    data = request.json
    logger.info(f"set_axis {data}")
    app.context.set_axis_data(bytearray(data))
    return {"status": "ok"}

@app.post("/autocal")
async def autocal(request):
    logger.info("autocal")
    await app.context.command_queue.async_put("autocal")
    return {"status": "ok"}

@click.group()
@click.option("--interface", default="socketcan", help="can interface")
@click.option("--channel", default="can0", help="can channel")
@click.option("--jtecu_id", default=0x01, help="JTECU number")
@click.option("--host", default="localhost", help="host")
@click.option("--port", default=8080, help="port")
@click.pass_context
def main(
    ctx,
    interface: str,
    channel: str,
    jtecu_id: int,
    host: str,
    port: int,
):
    ctx.obj = Context(
        interface=interface,
        channel=channel,
        jtecu_id=jtecu_id,
        host=host,
        port=port,
    )
    app.context = ctx.obj

@main.command()
@click.pass_obj
def serve(
    ctx,
):
    """
    Start the JTECU control server.
    """
    async def run():

        # Maintain JTECU mode
        async def service_jtecu():
            with ctx.bus() as bus:
                while True:
                    TCAN_MODE_REFRESH_PERIOD_S = 0.1
                    await asyncio.sleep(TCAN_MODE_REFRESH_PERIOD_S)

                    # Keep the JTECU in the current mode
                    msg = can.Message(
                        arbitration_id=0x500 + ctx.jtecu_id,
                        data=[ctx.teleo_mode],
                        is_extended_id=False,
                    )
                    bus.send(msg)

                    # Send commanded Axis values
                    msg = can.Message(
                        arbitration_id=0x560 + ctx.jtecu_id,
                        data=list(ctx.axis_data),
                        is_extended_id=False,
                    )
                    bus.send(msg)
        
        async def handle_command_queue():
            while True:
                command = await ctx.command_queue.async_get()
                print(f"handling command: {command}")

                if command == "autocal":

                    AUTOCAL_COMMAND_VAL = 0xFF01
                    AUTOCAL_COMMAND_MSB_INDEX = 2
                    AUTOCAL_COMMAND_LSB_INDEX = 3

                    data = bytearray(8)
                    data[AUTOCAL_COMMAND_MSB_INDEX] = (AUTOCAL_COMMAND_VAL >> 8) & 0xFF
                    data[AUTOCAL_COMMAND_LSB_INDEX] = AUTOCAL_COMMAND_VAL & 0xFF

                    # Send autocal command
                    with ctx.bus() as bus:
                        msg = can.Message(
                            arbitration_id=0x550 + ctx.jtecu_id,
                            data=data,
                            is_extended_id=False,
                        )
                        bus.send(msg)
                    
                else:
                    logger.error(f"Unknown command: {command}")


        async def send_some_ids():
            IDS_TO_SEND = [

                0x00000003,

                0x08000001,
                0x08000002,
                0x08000003,
                0x08000004,
                0x08000005,

                0x08000066,
                0x08000067,
                0x08000068,
                0x08000069,
                0x08000070,
                0x08000071,

                0x05800001,
            ]

            DELAY_MS = 500

            while True:
                await asyncio.sleep(DELAY_MS / 1000)
                with ctx.bus() as bus:
                    for id in IDS_TO_SEND:
                        msg = can.Message(
                            arbitration_id=id,
                            data=int.to_bytes(id, 8, byteorder="big"),
                            is_extended_id=True,
                        )
                        bus.send(msg)
                        print(f"sent {id}")


        # Start the JTECU servicing task
        task_service_jtecu = asyncio.create_task(service_jtecu())

        # Start the command queue handling task
        task_command_queue = asyncio.create_task(handle_command_queue())

        # A task to send a few random CAN IDs
        task_send_some_ids = asyncio.create_task(send_some_ids())

        # Start the REST server task
        server = asyncio.create_task(app.start_server(
            host=ctx.host,
            port=ctx.port,
        ))
        print(f"Running on {ctx.host}:{ctx.port}")

        await asyncio.gather(
            server,
            task_service_jtecu,
            task_command_queue,
            task_send_some_ids,
        )

    ctx.loop.run_until_complete(run())



@main.command()
@click.pass_obj
def enter_remote(
    ctx,
):
    """
    Enter remote control mode.
    """
    # post to the REST API

    url = f"http://{ctx.host}:{ctx.port}/enter_mode/{SystemMode.REMOTE}"
    response = requests.post(url)
    logger.info(response.json())

    if response.status_code == 200:
        logger.info("Entered remote control mode")
    else:
        logger.error("Failed to enter remote control mode")

@main.command()
@click.option("--mode", type=click.Choice(["manual", "remote"]), default=None, help="switch to the specified mode")
@click.option("--steering", type=int, default=None, help="steering value")
@click.pass_obj
def set(
    ctx,
    mode: str | None,
    steering: int | None,
):
    """
    Set options.
    """

    if mode is None and steering is None:
        logger.warning("No options specified")

    if mode is not None:
        match mode:
            case "manual":
                url = f"http://{ctx.host}:{ctx.port}/enter_mode/{SystemMode.MANUAL}"
            case "remote":
                url = f"http://{ctx.host}:{ctx.port}/enter_mode/{SystemMode.REMOTE}"
            case _:
                logger.error("Invalid mode")
                exit(1)
            
        response = requests.post(url)
        logger.info(response.json())

        if response.status_code == 200:
            logger.info(f"Entered {mode} mode")
        else:
            logger.error(f"Failed to enter {mode} mode")


    if steering is not None:
        if steering < -1000 or steering > 1000:
            logger.error("Invalid steering value")
            exit(1)
        
        url = f"http://{ctx.host}:{ctx.port}/set_axis"


        data = bytearray(8)
        data[0:2] = steering.to_bytes(2, byteorder="big", signed=True)
        response = requests.post(url, json=list(data))

        logger.info(response.json())

        if response.status_code == 200:
            logger.info(f"Set steering to {steering}")
        else:
            logger.error("Failed to set steering")


@main.command()
@click.pass_obj
def autocal(
    ctx,
):
    """
    Initiate the autocalibration process.
    """
    url = f"http://{ctx.host}:{ctx.port}/autocal"
    response = requests.post(url)
    logger.info(response.json())

    if response.status_code == 200:
        logger.info("Autocal initiated")
    else:
        logger.error("Failed to initiate autocal")


if __name__ == '__main__':
    main()
