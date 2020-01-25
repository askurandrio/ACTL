from typing import Any

from dataclasses import dataclass


@dataclass
class NamedResult:
	arg: str
	value: Any
