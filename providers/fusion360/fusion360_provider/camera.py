from typing import Optional

from codetocad.interfaces import CameraInterface

from codetocad.codetocad_types import *
from codetocad.utilities import *
from codetocad.core import *
from codetocad.enums import *


from . import Entity


class Camera(Entity, CameraInterface):
    name: str
    description: Optional[str] = None
    native_instance = None

    def __init__(
        self, name: str, description: Optional[str] = None, native_instance=None
    ):
        self.name = name
        self.description = description
        self.native_instance = native_instance

    def create_perspective(self):
        print(
            "create_perspective called:",
        )
        return self

    def create_orthogonal(self):
        print(
            "create_orthogonal called:",
        )
        return self

    def set_focal_length(self, length: float):
        print("set_focal_length called:", length)
        return self
