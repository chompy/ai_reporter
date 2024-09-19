from typing import Optional, Self, Union
from enum import StrEnum

class PropertyType(StrEnum):
    STR = "string"
    INT = "integer"
    FLOAT = "number"
    DICT = "object"
    LIST = "array"
    BOOL = "boolean"
    ENUM = "enum"

class PropertyDefinition:

    """ Defines a property value and its constraints. """

    def __init__(
        self,
        name : str,
        type : Union[PropertyType, str] = PropertyType.STR,
        description : str = "",
        min : Optional[int] = 0,
        max : Optional[int] = 0,
        choices : Optional[list[str]] = [],
        required : bool = False
    ):
        self.name = name
        self.type = PropertyType(type)
        self.description = description
        self.min = min
        self.max = max
        self.choices = choices
        self.required = required

    @classmethod
    def from_dict(cls,  data : dict[str,dict]) -> list[Self]:
        out = []
        for k, v in data.items():
            out.append(cls(name=k, **v))
        return out

    def to_dict(self) -> dict[str,object]:
        out : dict[str,object] = {
            "type": str(PropertyType.STR) if self.type == PropertyType.ENUM else str(self.type),
            "description": self.description
        }
        match self.type:
            case PropertyType.INT | PropertyType.FLOAT:
                if self.min: out["minimum"] = self.min
                if self.max: out["maximum"] = self.max
            case PropertyType.LIST:
                # TODO allow other list item data types
                out["items"] = {
                    "type": "string"
                }
            case PropertyType.ENUM:
                out["enum"] = self.choices
        return out
