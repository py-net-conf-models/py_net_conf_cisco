from copy import copy
from ipaddress import IPv4Interface
from pathlib import Path
from typing import Optional, Union

from ciscoconfparse2 import CiscoConfParse

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

    def _unexpected_config_line(self, line):
        raise ValueError(f"Unexpected config line: {line.text}")

    def get_interface(self, interface: InterfaceConfig) -> InterfaceConfig:
        """Return an InterfaceConfig object of the interface configuration"""
        found = InterfaceConfig(
            copy(interface.interface_type),
            interface.interface_number,
            interface.subinterface_number,
        )
        interface_text = interface.interface_line()
        interface_lines = self._parsed_config.find_objects(interface_text)
        interfaces_found = len(interface_lines)
        if interfaces_found == 1:
            for line in interface_lines[0].children:
                line_split = line.text.split()
                # Handle lines starting with " ip address"
                if line.re_search(r"\s+ip\s+address\s"):
                    if line_split[2] == "dhcp":
                        found.dhcp_assigned = True
                    elif len(line_split) == 4:
                        found.dhcp_assigned = False
                        found.ip_address = IPv4Interface(
                            f"{line_split[2]}/{line_split[3]}"
                        )
                    elif len(line_split) == 5:
                        if line_split[4] == "secondary":
                            found.secondary_ip_addreses.append(
                                IPv4Interface(
                                    f"{line_split[2]}/{line_split[3]}"
                                )
                            )
                        else:
                            self._unexpected_config_line(line.text)
                    else:
                        self._unexpected_config_line(line.text)
                elif line.re_search(r"description\s+(\S.+)"):
                    found.description = " ".join(line_split[1:])
                elif line.re_search(r"^\s+shutdown"):
                    found.shutdown = True
                elif line.re_search(r"^\s+no shutdown"):
                    found.shutdown = False
                elif line.re_search(r"^\s+vrf forwarding"):
                    found.vrf = line_split[2]
                else:
                    self._unexpected_config_line(line.text)
        return found
