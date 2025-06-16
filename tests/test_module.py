"""
Testing modules structure
"""

from inspect import isclass

import pytest

import py_net_conf_cisco


def test_module_version_exists():
    assert type(py_net_conf_cisco.__version__) is str


classes = [
    py_net_conf_cisco.InterfaceConfig,
]


@pytest.mark.parametrize("cls", classes)
def test_module_imports(cls):
    assert isclass(cls)
