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

    def _find_interface_lines(self, interface: InterfaceConfig):
        interface_text = interface.interface_line()
        return self._parsed_config.find_objects(interface_text)

    def get_interface(self, interface: InterfaceConfig) -> InterfaceConfig:
        """Return an InterfaceConfig object of the interface configuration"""
        found = InterfaceConfig(
            copy(interface.interface_type),
            interface.interface_number,
            interface.subinterface_number,
        )
        interface_lines = self._find_interface_lines(interface)
        if len(interface_lines) == 1:
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
                            self._unexpected_config_line(line)
                    else:
                        self._unexpected_config_line(line)
                elif line.re_search(r"description\s+(\S.+)"):
                    found.description = " ".join(line_split[1:])
                elif line.re_search(r"^\s+shutdown"):
                    found.shutdown = True
                elif line.re_search(r"^\s+no shutdown"):
                    found.shutdown = False
                elif line.re_search(r"^\s+vrf forwarding"):
                    found.vrf = line_split[2]
                elif line.re_search(r"^\s+!.*"):
                    # Ignore lines htat have been commented out
                    continue
                else:
                    self._unexpected_config_line(line)
        else:
            self._unexpected_config_line(line)
        return found

    def set_interface(self, interface: InterfaceConfig) -> bool:
        interface_lines = self._find_interface_lines(interface)
        if len(interface_lines) == 1:
            for line in interface_lines[0].children:
                line_split = line.text.split()
                # Handle lines starting with " ip address"
                if line.re_search(r"\s+ip\s+address\s"):
                    if line_split[2] == "dhcp":
                        if interface.dhcp_assigned is False:
                            line.re_sub(
                                r"dhcp.*",
                                f"{str(interface.ip_address.ip)} {str(interface.ip_address.netmask)}",
                            )
                    elif len(line_split) == 4:
                        if interface.dhcp_assigned is True:
                            line.res_sub(r"\d.*", "dhcp")
                        else:
                            if line_split[2] != str(
                                interface.ip_address.ip
                            ) or line_split[3] != str(
                                interface.ip_address.netmask
                            ):
                                line.re_sub(
                                    r"\d.*",
                                    f"{interface.ip_address.ip} {interface.ip_address.netmask}",
                                )
                    elif len(line_split) == 5:
                        if line_split[4] == "secondary":
                            if len(interface.secondary_ip_addreses) == 0:
                                line.re_sub(r"\S.+", "!")
                            #         found.secondary_ip_addreses.append(
                            #             IPv4Interface(
                            #                 f"{line_split[2]}/{line_split[3]}"
                            #             )
                            #         )
                            #     else:
                            #         self._unexpected_config_line(line.text)
                            # else:
                            #     self._unexpected_config_line(line.text)
                elif line.re_search(r"description\s+(\S.+)"):
                    line.re_sub(
                        r"description.*",
                        f"description {interface.description}",
                    )
                elif (
                    line.re_search(r"^\s+shutdown")
                    and interface.shutdown is False
                ):
                    line.re_sub(r"shutdown", "no shutdown")
                elif (
                    line.re_search(r"^\s+no shutdown")
                    and interface.shutdown is True
                ):
                    line.re_sub(r"no ", "")
                elif line.re_search(r"^\s+vrf forwarding"):
                    if interface.vrf != line_split[2]:
                        line.re_sub(r"vrf.*", f"vrf forwarding {interface.vrf}")
                else:
                    self._unexpected_config_line(line.text)
        else:
            self._unexpected_config_line(line.text)
        self._parsed_config.commit()
        return True
