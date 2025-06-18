import os
import tempfile
from ipaddress import IPv4Interface

import pytest
import sample1

from py_net_conf_cisco import CiscoConfig, InterfaceConfig
from py_net_conf_cisco.interface_datamodel import InterfaceType


class TestCiscoConfig:
    """
    Test class for the CiscoConfig module
    """

    def test_empty_creationi_fails(self):
        with pytest.raises(ValueError):
            config = CiscoConfig()
            return config

    def test_init_with_text(self):
        """Test initialization with config text."""
        config = CiscoConfig(config_text=sample1.config)
        assert config._parsed_config is not None

    @pytest.fixture
    def sample_config_file(self):
        """Create a temporary configuration file for testing."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".cfg", delete=False
        ) as f:
            f.write(sample1.config)
            temp_path = f.name

        yield temp_path

        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    @pytest.fixture
    def config_from_file(self, sample_config_file):
        """Create CiscoConfig instance from file."""
        return CiscoConfig(config_path=sample_config_file)

    @pytest.fixture
    def empty_config(self):
        """Create and empty config"""
        return CiscoConfig(config_text="!")

    def test_init_with_file(self, sample_config_file):
        """Test initialization with config file."""
        config = CiscoConfig(config_path=sample_config_file)
        assert config._parsed_config is not None

    def find_hostname_line(self, parsed_config):
        return parsed_config.find_objects(r"^hostname\s+")[0]

    def test_seting_hostname_property_with_sample1(self, config_from_file):
        """Test setting the hostname"""
        config_from_file.hostname = "foo"
        assert config_from_file.hostname == "foo"
        hostname_line = self.find_hostname_line(config_from_file._parsed_config)
        assert hostname_line.text == "hostname foo"

    def test_getting_hostname_property(self, config_from_file):
        """Test the hostname propeerty"""
        hostname = config_from_file.hostname
        assert hostname == "TestSwitch"
        hostname_line = self.find_hostname_line(config_from_file._parsed_config)
        assert hostname_line.text == "hostname TestSwitch"

    def test_seting_hostname_property_with_no_hostname_version_line(
        self, config_from_file
    ):
        """Test setting the hostname when there is not a hostname configured
        but there is a version line"""
        hostname_line = self.find_hostname_line(config_from_file._parsed_config)
        hostname_line.delete()
        config_from_file._parsed_config.commit()
        config_from_file.hostname = "foo"
        assert config_from_file.hostname == "foo"
        hostname_line = self.find_hostname_line(config_from_file._parsed_config)
        assert hostname_line.text == "hostname foo"

    def test_setting_hostname_property_with_empty_config(self, empty_config):
        empty_config.hostname = "foo"
        assert empty_config.hostname == "foo"
        hostname_line = self.find_hostname_line(empty_config._parsed_config)
        assert hostname_line.text == "hostname foo"
        assert len(empty_config._parsed_config.get_text()) == 2

    @pytest.mark.parametrize(
        "interface,expected",
        [
            (
                InterfaceConfig(
                    interface_type=InterfaceType.VLAN,
                    interface_number="10",
                ),
                InterfaceConfig(
                    interface_type=InterfaceType.VLAN,
                    interface_number="10",
                    description="Server VLAN",
                    ip_address=IPv4Interface("10.0.10.1/24"),
                    dhcp_assigned=False,
                ),
            ),
            (
                InterfaceConfig(
                    interface_type=InterfaceType.GIGABITETHERNET,
                    interface_number="0/3",
                ),
                InterfaceConfig(
                    interface_type=InterfaceType.GIGABITETHERNET,
                    interface_number="0/3",
                    description="DHCP Test Interface",
                    ip_address=None,
                    dhcp_assigned=True,
                ),
            ),
        ],
    )
    def test_getting_interface(self, config_from_file, interface, expected):
        assert config_from_file.get_interface(interface) == expected
