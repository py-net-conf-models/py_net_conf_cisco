import os
import tempfile

import pytest
import sample1

from py_net_conf_cisco import CiscoConfig


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

    def test_init_with_file(self, sample_config_file):
        """Test initialization with config file."""
        config = CiscoConfig(config_path=sample_config_file)
        assert config._parsed_config is not None
