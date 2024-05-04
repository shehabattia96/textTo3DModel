# THIS IS AN AUTO-GENERATE FILE.
# DO NOT EDIT MANUALLY.
# Please run development/capabilities_json_to_python/capabilities_to_py.sh to generate this file.
# Copy this file and remove this header to create a new CodeToCAD Provider.

from codetocad.codetocad_types import *


from codetocad.interfaces.vertex_interface import VertexInterface


from codetocad.interfaces.entity_interface import EntityInterface


from providers.sample.entity import Entity


class Vertex(VertexInterface, Entity):
    def __init__(
        self,
        name: "str",
        location: "Point",
        description: "str| None" = None,
        native_instance=None,
        parent_entity: "str|Entity| None" = None,
    ):
        self.name = name
        self.location = location
        self.description = description
        self.native_instance = native_instance
        self.parent_entity = parent_entity

    def get_control_points(
        self,
    ) -> "list[Vertex]":
        print(
            "get_control_points called",
        )

        return [Vertex("a vertex", Point.from_list_of_float_or_string([0, 0, 0]))]

    def project(self, project_from: "ProjectableInterface") -> "ProjectableInterface":
        print("project called", f": {project_from}")

        return __import__("codetocad").Sketch("a projected sketch")
