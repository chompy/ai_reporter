from typing import Optional, Self, Union, Any
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
        # TODO allow import of JSON schema (https://json-schema.org/)
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

    def check_type(self, value : Any) -> bool:
        """
        Check if given value matches property type.

        :param value: Value to check.
        """
        match self.type:
            case PropertyType.STR:
                return isinstance(value, str)
            case PropertyType.INT:
                return isinstance(value, int)
            case PropertyType.FLOAT:
                return isinstance(value, float)
            case PropertyType.BOOL:
                return isinstance(value, bool)
            case PropertyType.DICT:
                return isinstance(value, dict)
            case PropertyType.LIST | PropertyType.ENUM:
                return isinstance(value, list)

    def check_required(self, value : Any) -> bool:
        """
        Check if required value is not none.

        :param value: Value to check.
        """
        return value is not None or not self.required

    def check_range(self, value : Any) -> bool:
        """
        Check if given value is in range.

        :param value: Value to check.
        """
        if self.min and value < self.min: return False
        if self.max and value > self.max: return False
        return True

    def check_choices(self, value : Any) -> bool:
        """
        Check if given value is a valid choice.

        :param value: Value to check.
        """
        return not self.choices or value in self.choices