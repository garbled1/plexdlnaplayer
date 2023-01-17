from pydantic import BaseSettings
from pathlib import Path
import json


class Settings(BaseSettings):
    http_port = 32488
    host_ip: str = None
    product = "Plex DLNA Player"
    aliases: str = ""
    location_url: str = None
    version = "1"
    platform = "Linux"
    platform_version = "1"
    plex_notify_interval = 0.5
    config_path = "config"
    data_file_name = "data.json"
    location_port_file_name = "dlna_servers.json"
    device_ports = []
    base_port = 32489

    def dlna_name_alias(self, uuid: str, name: str, ip: str):
        data = self.load_data(self.data_file_name)
        alias = data.get(uuid, {}).get('alias', None)
        if alias is not None:
            return alias
        if not settings.aliases:
            return name
        aliases = settings.aliases.split(",")
        for alias in aliases:
            k, v = alias.split(":")
            if k.strip() in [uuid.strip(), name.strip(), ip.strip()]:
                return v.strip()
        return name

    def save_dlna_name_alias(self, uuid, alias):
        data = self.load_data(self.data_file_name)
        info = data.get(uuid, {})
        info['alias'] = alias
        data[uuid] = info
        self.save_data(data, self.data_file_name)

    def load_dlna_location_port(self, location):
        data = self.load_data(self.location_port_file_name)
        location = data.get(location, {})
        return location.get('port',None)
    def load_dlna_locations(self):
        return self.load_data(self.location_port_file_name)

    def save_dlna_location_port(self, location, port):
        data = self.load_data(self.location_port_file_name)
        info = data.get(location, {})
        info['port'] = port
        data[location] = info
        self.save_data(data, self.location_port_file_name)

    def load_data(self, config_file_name):
        p = Path(self.config_path).joinpath(config_file_name)
        p.parent.mkdir(parents=True, exist_ok=True)
        if not p.exists():
            return {}
        try:
            with open(p) as f:
                j = json.load(f)
                return j
        except Exception:
            return {}

    def save_data(self, data, config_file_name):
        p = Path(self.config_path).joinpath(config_file_name)
        p.parent.mkdir(parents=True, exist_ok=True)
        if not p.exists():
            p.touch()
        with open(p, mode="w") as f:
            json.dump(data, f, indent=4)

    def get_token_for_uuid(self, uuid):
        d = self.load_data(self.data_file_name)
        return d.get(uuid, {}).get("token", None)

    def set_token_for_uuid(self, uuid, token):
        d = self.load_data(self.data_file_name)
        info = d.get(uuid, {})
        info['token'] = token
        d[uuid] = info
        self.save_data(d,self.data_file_name)

    def allocate_new_port(self):
        """Allocate a new port, append to array."""
        self.base_port = self.get_max_port_from_settings(self.base_port)
        new_port = self.base_port + 1
        self.device_ports.append(new_port)
        return new_port

    def get_max_port_from_settings(self, default_port):
        data = self.load_dlna_locations()
        max_port = default_port
        for location in data.values():
            if location['port'] > max_port:
                max_port = location['port']
        return max_port


settings = Settings()
