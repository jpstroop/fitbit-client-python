# fitbit_client/utils/types.py

# Standard library imports
from typing import Dict
from typing import List
from typing import TypeAlias

JSONType: TypeAlias = Dict[str, "JSONType"] | List["JSONType"] | str | int | float | bool | None
