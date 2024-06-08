from typing import Optional
from codetocad.utilities.supported import supported
from codetocad.enums.support_level import SupportLevel
from codetocad.interfaces.light_interface import LightInterface
from providers.fusion360.fusion360_provider.entity import Entity
from . import Entity


class Light(LightInterface, Entity):
    name: str
    description: Optional[str] = None
    native_instance = None

    def __init__(
        self, name: "str", description: "str| None" = None, native_instance=None
    ):
        self.name = name
        self.description = description
        self.native_instance = native_instance

    @supported(SupportLevel.UNSUPPORTED)
    def set_color(
        self, r_value: "int|float", g_value: "int|float", b_value: "int|float"
    ):
        print("set_color called:", r_value, g_value, b_value)
        return self

    @supported(SupportLevel.UNSUPPORTED)
    def create_sun(self, energy_level: "float"):
        print("create_sun called:", energy_level)
        return self

    @supported(SupportLevel.UNSUPPORTED)
    def create_spot(self, energy_level: "float"):
        print("create_spot called:", energy_level)
        return self

    @supported(SupportLevel.UNSUPPORTED)
    def create_point(self, energy_level: "float"):
        print("create_point called:", energy_level)
        return self

    @supported(SupportLevel.UNSUPPORTED)
    def create_area(self, energy_level: "float"):
        print("create_area called:", energy_level)
        return self
