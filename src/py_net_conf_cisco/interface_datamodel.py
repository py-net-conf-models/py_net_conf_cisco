"""
Data models for Cisco interface configuration options.

This module provides dataclasses and enums for structuring interface configuration options.
"""

from dataclasses import dataclass, field
from enum import Enum
from ipaddress import IPv4Interface
from typing import Optional


class InterfaceType(Enum):
    """
    Allowabld interface types
    """

    ETHERNET = "Ethernet"
    GIGABITETHERNET = "GigabitEthernet"
    TENGIGABITETHERNET = "TenGigabitEthernet"
    TWENTYFIVEGIGABITETHERNET = "TwentyFiveGigE"
    FORTYGIGABITETHERNET = "FortyGigabitEthernet"
    HUNDREDGIGABITETHERNET = "HundredGigE"
    VLAN = "Vlan"
    LOOPBACK = "loopback"
    PORT_CHANNEL = "port-channel"
    NVE = "nve"


@dataclass
class InterfaceConfig:
    """
    Represents an interface configuration.

    Attributes:
            interface_type: The type of interface (e.g., GigabitEthernet).
            interface_number: The number of the interface as a string (e.g., 1/1/1).
            subinterface_number: Optional subinterface number.
            ip_address: Optional IPv4 interface address (ipaddress.IPv4Interface).
            vrf: Optional VRF assignment as a string.
            dhcp_assigned: If True, IP address is assigned by DHCP.
            description: Optional interface description.
            shutdown: If True, the interface is administratively shut down.
            secondary_ip_addreses: Optional list of secondary  IPv4 interface address (ipaddress.IPv4Interface).
    """

    interface_type: InterfaceType
    interface_number: str
    subinterface_number: Optional[int] = None
    ip_address: Optional[IPv4Interface] = None
    vrf: Optional[str] = None
    dhcp_assigned: Optional[bool] = None
    description: Optional[str] = None
    shutdown: Optional[bool] = None
    secondary_ip_addreses: list[IPv4Interface] = field(default_factory=list)

    def __post_init__(self):
        # Verify that the ip address the interface has is either DHCP or staticall assigned.
        if any(
            [
                self.dhcp_assigned is True and self.ip_address is not None,
                self.dhcp_assigned is False and self.ip_address is None,
            ]
        ):
            raise Exception

    def interface_line(self):
        """Return the the parent line for the interface configuration"""
        return f"interface {self.interface_type.value}{self.interface_number}{'' if self.subinterface_number is None else '.' + str(self.subinterface_number)}"

    def to_config_lines(self):
        """
        Render the interface configuration as Cisco-style CLI lines.
        """
        lines = [self.interface_line()]
        if self.description is not None:
            lines.append(f" description {self.description}")
        if self.vrf is not None:
            lines.append(f" vrf forwarding {self.vrf}")
        if self.ip_address is not None:
            lines.append(
                f" ip address {str(self.ip_address.ip)} {str(self.ip_address.netmask)}"
            )
        elif self.dhcp_assigned:
            lines.append(" ip address dhcp")
        if self.shutdown is not None:
            lines.append(" shutdown")
        lines.append("!")
        return lines
