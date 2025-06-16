from pathlib import Path
from typing import Optional, Union

from ciscoconfparse2 import CiscoConfParse


class CiscoConfig:
    def __init__(
        self,
        config_path: Optional[Union[str, Path]] = None,
        config_text: Optional[str] = None,
    ):
        self._hostname = None
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
                self._hostname = hostname_objs[0].text.split()[1]
            else:
                self._hostname = ""
        return self._hostname
