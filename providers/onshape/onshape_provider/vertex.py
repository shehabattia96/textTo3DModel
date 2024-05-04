from typing import Optional
from codetocad.interfaces.vertex_interface import VertexInterface
from codetocad.interfaces.projectable_interface import ProjectableInterface
from providers.onshape.onshape_provider.entity import Entity
from codetocad.codetocad_types import *


class Vertex(VertexInterface, Entity):
    def project(self, project_from: "ProjectableInterface") -> "Projectable":
        raise NotImplementedError()

    location: str | list[str] | list[float] | list[Dimension] | Point
    parent_entity: Optional[str | Entity] = None
    name: str
    description: Optional[str] = None
    native_instance = None

    def __init__(
        self,
        name: "str",
        location: "Point",
        description: "str| None" = None,
        native_instance=None,
        parent_entity: "str|Entity| None" = None,
    ):
        self.location = location
        self.parent_entity = parent_entity
        self.name = name
        self.description = description
        self.native_instance = native_instance

    def get_control_points(self) -> "list[Entity]":
        raise NotImplementedError()

    @property
    def _center(self):
        return self.location
