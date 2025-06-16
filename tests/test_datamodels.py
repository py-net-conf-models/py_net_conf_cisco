"""
Test suite for the interface datamodels.
"""

import ipaddress
from ipaddress import IPv4Interface

from pytest import raises

from py_net_conf_cisco.interface_datamodel import InterfaceConfig, InterfaceType


class TestInterfaceConfig:
    """Test class for the InterfaceConfig dataclass."""

    def test_empty_creation_throws_excptions(self):
        """Test a empty creation fails"""
        with raises(TypeError):
            interface = InterfaceConfig()  # pyright: ignore
            return interface

    def test_creation_with_no_interface_type_throws_exception(self):
        """Test a creation with no InterfaceType failes"""
        with raises(TypeError):
            interface = InterfaceConfig(interface_number="1")  # pyright: ignore
            return interface

    def test_creation_with_no_number_type_throws_exception(self):
        """Test a creation with no InterfaceType failes"""
        with raises(TypeError):
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
        with raises(Exception):
            interface = InterfaceConfig(
                interface_type=InterfaceType.ETHERNET,
                interface_number="1",
                dhcp_assigned=True,
                ip_address=IPv4Interface("1.1.1.1/24"),
            )
            return interface

    def test_interface_with_false_dhcp_and_no_ip_fails(self):
        """Test the IP address and DHCP fails"""
        with raises(Exception):
            interface = InterfaceConfig(
                interface_type=InterfaceType.ETHERNET,
                interface_number="1",
                dhcp_assigned=False,
            )
            return interface

    def test_to_config_lines_minimal(self):
        interface = InterfaceConfig(
            interface_type=InterfaceType.ETHERNET,
            interface_number=1,  # pyright: ignore
        )
        expected_lines = ["interface Ethernet1", "!"]
        assert expected_lines == interface.to_config_lines()

    def test_to_config_lines_with_subinterface(self):
        interface = InterfaceConfig(
            interface_type=InterfaceType.ETHERNET,
            interface_number="1",
            subinterface_number=2,
        )
        expected_lines = ["interface Ethernet1.2", "!"]
        assert expected_lines == interface.to_config_lines()

    def test_to_config_lines_with_description(self):
        interface = InterfaceConfig(
            interface_type=InterfaceType.ETHERNET,
            interface_number="1",
            description="Test description",
        )
        expected_lines = [
            "interface Ethernet1",
            " description Test description",
            "!",
        ]
        assert expected_lines == interface.to_config_lines()

    def test_to_config_lines_with_ip_address(self):
        interface = InterfaceConfig(
            interface_type=InterfaceType.ETHERNET,
            interface_number="1",
            ip_address=ipaddress.IPv4Interface("1.1.1.1/24"),
        )
        expected_lines = [
            "interface Ethernet1",
            " ip address 1.1.1.1 255.255.255.0",
            "!",
        ]
        assert expected_lines == interface.to_config_lines()

    def test_to_config_lines_with_vrf_and_ip_address(self):
        interface = InterfaceConfig(
            interface_type=InterfaceType.ETHERNET,
            interface_number="1",
            ip_address=ipaddress.IPv4Interface("1.1.1.1/24"),
            vrf="test",
        )
        expected_lines = [
            "interface Ethernet1",
            " vrf forwarding test",
            " ip address 1.1.1.1 255.255.255.0",
            "!",
        ]
        assert expected_lines == interface.to_config_lines()

    def test_to_config_lines_with_dhcp_address(self):
        interface = InterfaceConfig(
            interface_type=InterfaceType.ETHERNET,
            interface_number="1",
            dhcp_assigned=True,
        )
        expected_lines = [
            "interface Ethernet1",
            " ip address dhcp",
            "!",
        ]
        assert expected_lines == interface.to_config_lines()

    def test_to_config_lines_with_shutdown(self):
        interface = InterfaceConfig(
            interface_type=InterfaceType.ETHERNET,
            interface_number="1",
            shutdown=True,
        )
        expected_lines = [
            "interface Ethernet1",
            " shutdown",
            "!",
        ]
        assert expected_lines == interface.to_config_lines()
