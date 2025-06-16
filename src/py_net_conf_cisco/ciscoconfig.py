from ipaddress import IPv4Interface
from pathlib import Path
from typing import Optional, Union

from ciscoconfparse2 import CiscoConfParse
from ciscoconfparse2.ccp_util import IPv4Obj

from .interface_datamodel import InterfaceConfig


class CiscoConfig:
    def __init__(
        self,
        config_path: Optional[Union[str, Path]] = None,
        config_text: Optional[str] = None,
    ):
        self._hostname = None
        self._hostname_line = None
        if config_path is None and config_text is None:
            raise ValueError(
                "Either config_path or config_text must be provided"
            )

        if config_text is not None:
            config_lines = config_text.splitlines()
            self._parsed_config = CiscoConfParse(config_lines)
        else:
            self._parsed_config = CiscoConfParse(str(config_path))

    @property
    def hostname(self) -> str:
        if self._hostname is None:
            hostname_objs = self._parsed_config.find_objects(r"^hostname\s+")
            if hostname_objs:
                self._hostname_line = hostname_objs[0]
                self._hostname = self._hostname_line.text.split()[1]
            else:
                self._hostname = ""
        return self._hostname

    @hostname.setter
    def hostname(self, value: str) -> None:
        self._hostname = value
        if self._hostname_line:
            self._hostname_line.text = f"hostname {value}"
        else:
            version_objs = self._parsed_config.find_objects(r"^version\s+")
            if version_objs:
                version_objs[0].insert_after(f"hostname {value}")
            else:
                if self._parsed_config.objs:
                    self._parsed_config.objs[0].insert_before(
                        f"hostname {value}"
                    )
                else:
                    self._parsed_config = CiscoConfParse([f"hostname {value}"])

    def get_interface(self, interface: InterfaceConfig) -> InterfaceConfig:
        """Return an InterfaceConfig object of the interface configuration"""
        found = InterfaceConfig(
            interface.interface_type,
            interface.interface_number,
            interface.subinterface_number,
        )
        interface_text = interface.interface_line()
        interface_lines = self._parsed_config.find_objects(interface_text)
        if len(interface_lines) < 0:
            return found
        ipv4_addresses = interface_lines[0].re_list_iter_typed(
            r"ip\s+address\s+(\S.+)", result_type=IPv4Obj
        )
        if ipv4_addresses:
            found.ip_address = IPv4Interface(
                f"{str(ipv4_addresses[0].ip)}/{ipv4_addresses[0].prefixlen}"
            )
        descriptions = interface_lines[0].re_list_iter_typed(
            r"description\s+(\S.+)", result_type=str
        )
        if descriptions:
            found.description = descriptions[0]
        return found
