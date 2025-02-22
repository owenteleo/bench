import yaml

from loguru import logger
from collections import namedtuple

CanBusSpec = namedtuple("CanBusSpec", ["interface", "channel"])

class Configuration:
    VERSION_STRING = "bench-cfg-v1"

    class Builder:
        """
        Configuration builder.
        """
        @staticmethod
        def from_dict(data):
            """
            Creates a builder from a dictionary of configuration data.
            """
            builder = Configuration.Builder()

            if "version" not in data:
                raise ValueError("Configuration does not have a version.")
            if data["version"] != "bench-cfg-v1":
                raise ValueError(f"Unsupported configuration version: {data['version']} (supported config format versions: {[ 'bench-cfg-v1' ]}).")
        
            if "server" in data:
                server = data["server"]

                if "host" in server:
                    builder.with_host(server["host"])

                if "port" in server:
                    builder.with_port(server["port"])

            if "tcan" in data:
                tcan = data["tcan"]
                if "channel" not in tcan:
                    raise ValueError("tcan configuration must have a 'channel' key.")
                if "interface" not in tcan:
                    raise ValueError("tcan configuration must have an 'interface' key.")
                
                builder.with_tcan(tcan["interface"], tcan["channel"])

            if "mcan" in data:
                mcan = data["mcan"]
                if "channel" not in mcan:
                    raise ValueError("mcan configuration must have a 'channel' key.")
                if "interface" not in mcan:
                    raise ValueError("mcan configuration must have an 'interface' key.")

                builder.with_mcan(mcan["interface"], mcan["channel"])
            
            if "busses" in data:
                busses = data["busses"]
                for bus in busses:
                    if "name" not in bus:
                        raise ValueError("Bus configuration must have a 'name' key.")
                    if "channel" not in bus:
                        raise ValueError("Bus configuration must have a 'channel' key.")
                    if "interface" not in bus:
                        raise ValueError("Bus configuration must have an 'interface' key.")
                
                    name = bus["name"]
                    if name in builder.registered_busses:
                        logger.warning(f"Bus {name} is already registered. Overwriting.")
            
                    builder.with_additional_bus(name, bus["interface"], bus["channel"])

            return builder

        def __init__(self):
            self._host = "localhost"
            self._port = 8080
            self._mcan = None
            self._tcan = None
            self._busses = {}
        
        @property
        def registered_busses(self):
            return [name for name in self._busses.keys()]

        def with_host(self, host):
            self._host = host
            return self
    
        def with_port(self, port):
            self._port = port
            return self
        
        def with_tcan(self, interface, channel):
            self._tcan = CanBusSpec(interface, channel)
            return self
    
        def with_mcan(self, interface, channel):
            self._mcan = CanBusSpec(interface, channel)
            return self
        
        def with_additional_bus(self, name, interface, channel):
            self._busses[name] = CanBusSpec(interface, channel)
            return self
        
        def build(self):
            return Configuration(
                host=self._host,
                port=self._port,
                tcan=self._tcan,
                mcan=self._mcan,
                busses=self._busses,
            )

    """
    Testbench configuration.
    """
    @staticmethod
    def deserialize(input):
        """
        Deserializes the configuration.
        """
        data = yaml.safe_load(input)
        return Configuration.Builder.from_dict(data).build()
    
    @staticmethod
    def serialize(config, stream=None):
        """
        Serializes the configuration.
        """
        data = {}
        data["version"] = Configuration.VERSION_STRING
        data["server"] = {
            "host": config.host,
            "port": config.port,
        }
        if config.tcan is not None:
            data["tcan"] = {
                "interface": config.tcan.interface,
                "channel": config.tcan.channel,
            }
        if config.mcan is not None:
            data["mcan"] = {
                "interface": config.mcan.interface,
                "channel": config.mcan.channel,
            }
        if config.busses:
            data["busses"] = [
                {
                    "name": name,
                    "interface": bus.interface,
                    "channel": bus.channel,
                }
                for name, bus in config.busses.items()
            ]

        return yaml.dump(data, stream, sort_keys=False)

    @staticmethod
    def builder():
        return Configuration.Builder()

    def __init__(self, host, port, tcan, mcan, busses):
        self._host = host
        self._port = port
        self._tcan = tcan
        self._mcan = mcan
        self._busses = busses

    @property
    def host(self):
        return self._host
    
    @property
    def port(self):
        return self._port
    
    @property
    def tcan(self):
        return self._tcan
    
    @property
    def mcan(self):
        return self._mcan
    
    @property
    def busses(self):
        return self._busses
    
    def format(self, fmt):
        if fmt == "yaml":
            return Configuration.serialize(self)
        else:
            msg = f"Unsupported format: {fmt}"
            logger.error(msg)
            raise ValueError(msg)
        
    @property
    def get_bus(self, name):
        return self._busses[name] if name in self._busses else None
