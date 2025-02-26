# fitbit_client/utils/types.py

# Standard library imports
from typing import Dict
from typing import List
from typing import TypedDict
from typing import Union

# Define a generic type for JSON data
JSONPrimitive = Union[str, int, float, bool, None]
JSONType = Union[Dict[str, "JSONType"], List["JSONType"], JSONPrimitive]

# "Wrapper" types that at least give a hint at the outermost structure
JSONDict = Dict[str, JSONType]
JSONList = List[JSONType]

# Types for API parameter values
ParamValue = Union[str, int, float, bool, None]
ParamDict = Dict[str, ParamValue]


# Type definitions for token structure
class TokenDict(TypedDict, total=False):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    expires_at: float
    scope: List[str]
