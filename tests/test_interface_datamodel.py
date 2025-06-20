"""
Test suite for the interface datamodels.
"""

import ipaddress
from ipaddress import IPv4Interface

import pytest

from py_net_conf_cisco.interface_datamodel import InterfaceConfig, InterfaceType


class TestInterfaceConfig:
    """Test class for the InterfaceConfig dataclass."""

    def test_empty_creation_throws_excptions(self):
        """Test a empty creation fails"""
        with pytest.raises(TypeError):
            interface = InterfaceConfig()  # pyright: ignore
            return interface

    def test_creation_with_no_interface_type_throws_exception(self):
        """Test a creation with no InterfaceType failes"""
        with pytest.raises(TypeError):
            interface = InterfaceConfig(interface_number="1")  # pyright: ignore
            return interface

    def test_creation_with_no_number_type_throws_exception(self):
        """Test a creation with no InterfaceType failes"""
        with pytest.raises(TypeError):
            interface = InterfaceConfig(InterfaceType.ETHERNET)  # pyright: ignore
            return interface

    def test_basic_creation(self):
        """Test with only an InterfaceType"""
        interface = InterfaceConfig(
            InterfaceType.ETHERNET, interface_number="1"
        )
        assert interface is not None
        assert interface.ip_address is None
        assert interface.vrf is None
        assert interface.description is None
        assert interface.shutdown is None

    def test_interface_with_ip(self):
        """Test interface creation with IP address."""
        interface = InterfaceConfig(
            interface_type=InterfaceType.ETHERNET,
            interface_number="1",
            ip_address=IPv4Interface("1.1.1.1/24"),
        )
        assert interface.interface_type == InterfaceType.ETHERNET
        assert interface.ip_address == IPv4Interface("1.1.1.1/24")
        assert interface.dhcp_assigned is not True

    def test_interface_with_dhcp(self):
        """Test the IP address can be set with DHCP"""
        interface = InterfaceConfig(
            interface_type=InterfaceType.ETHERNET,
            interface_number="1",
            dhcp_assigned=True,
        )
        assert interface.interface_type == InterfaceType.ETHERNET
        assert interface.ip_address is None
        assert interface.dhcp_assigned

    def test_interface_with_dhcp_and_ip_fails(self):
        """Test the IP address and DHCP fails"""
        with pytest.raises(Exception):
            interface = InterfaceConfig(
                interface_type=InterfaceType.ETHERNET,
                interface_number="1",
                dhcp_assigned=True,
                ip_address=IPv4Interface("1.1.1.1/24"),
            )
            return interface

    def test_interface_with_false_dhcp_and_no_ip_fails(self):
        """Test the IP address and DHCP fails"""
        with pytest.raises(Exception):
            interface = InterfaceConfig(
                interface_type=InterfaceType.ETHERNET,
                interface_number="1",
                dhcp_assigned=False,
            )
            return interface

    @pytest.mark.parametrize(
        "kwargs,expected_lines",
        [
            (  # Test with minimal configuration
                {
                    "interface_type": InterfaceType.ETHERNET,
                    "interface_number": "1",
                },
                ["interface Ethernet1", "!"],
            ),
            (  # Test with an IP address
                {
                    "interface_type": InterfaceType.ETHERNET,
                    "interface_number": "1",
                    "ip_address": ipaddress.IPv4Interface("192.168.1.1/24"),
                },
                [
                    "interface Ethernet1",
                    " ip address 192.168.1.1 255.255.255.0",
                    "!",
                ],
            ),
            (  # Test with an IP address and a VRF)
                {
                    "interface_type": InterfaceType.ETHERNET,
                    "interface_number": "1",
                    "ip_address": ipaddress.IPv4Interface("1.1.1.1/24"),
                    "vrf": "test",
                },
                [
                    "interface Ethernet1",
                    " vrf forwarding test",
                    " ip address 1.1.1.1 255.255.255.0",
                    "!",
                ],
            ),
            (  # Test with DHCP address
                {
                    "interface_type": InterfaceType.ETHERNET,
                    "interface_number": "1",
                    "dhcp_assigned": True,
                },
                [
                    "interface Ethernet1",
                    " ip address dhcp",
                    "!",
                ],
            ),
            (  # Test with a description
                {
                    "interface_type": InterfaceType.ETHERNET,
                    "interface_number": 1,
                    "description": "Test description",
                },
                ["interface Ethernet1", " description Test description", "!"],
            ),
            (  # Test with shutdown
                {
                    "interface_type": InterfaceType.ETHERNET,
                    "interface_number": "1",
                    "shutdown": True,
                },
                ["interface Ethernet1", " shutdown", "!"],
            ),
            (  # Test with shutdown False
                {
                    "interface_type": InterfaceType.ETHERNET,
                    "interface_number": "1",
                    "shutdown": False,
                },
                ["interface Ethernet1", " no shutdown", "!"],
            ),
            (  # Test with secondary IPs
                {
                    "interface_type": InterfaceType.VLAN,
                    "interface_number": "10",
                    "ip_address": IPv4Interface("10.0.10.1/24"),
                    "secondary_ip_addresses": [
                        IPv4Interface("10.0.11.1/24"),
                        IPv4Interface("10.0.12.1/24"),
                    ],
                },
                [
                    "interface Vlan10",
                    " ip address 10.0.10.1 255.255.255.0",
                    " ip address 10.0.11.1 255.255.255.0 secondary",
                    " ip address 10.0.12.1 255.255.255.0 secondary",
                    "!",
                ],
            ),
        ],
    )
    def test_to_config_lines_various(self, kwargs, expected_lines):
        interface = InterfaceConfig(**kwargs)
        assert interface.interface_line() == expected_lines[0]
        assert interface.to_config_lines() == expected_lines
