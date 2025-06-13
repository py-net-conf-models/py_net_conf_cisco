"""
Data Models fo configuration options

This module provides dataclasses for structuring configuration options.
"""

from enum import Enum


class InterfaceType(Enum):
    """Allowabld interface types"""

    GIGABITETHERNET = "GigabitEthernet"
    TENGIGABITETHERNET = "TenGigabitEthernet"
    TWENTYFIVEGIGABITETHERNET = "TwentyFiveGigE"
    FORTYGIGABITETHERNET = "FortyGigabitEthernet"
    HUNDREDGIGABITETHERNET = "HundredGigE"
    VLAN = "Vlan"
    LOOPBACK = "loopback"
    PORT_CHANNEL = "port-channel"
    NVE = "nve"
