from typing import Optional
from codetocad.interfaces.entity_interface import EntityInterface
from codetocad.interfaces.edge_interface import EdgeInterface
from codetocad.interfaces.vertex_interface import VertexInterface
from providers.blender.blender_provider.part import Part
from codetocad.interfaces.wire_interface import WireInterface
from codetocad.interfaces.part_interface import PartInterface
from codetocad.interfaces.landmark_interface import LandmarkInterface
from providers.blender.blender_provider.blender_definitions import BlenderTypes
from providers.blender.blender_provider.entity import Entity
from providers.blender.blender_provider.vertex import Vertex
from providers.blender.blender_provider.landmark import Landmark
from providers.blender.blender_provider.edge import Edge
from codetocad.codetocad_types import *
from codetocad.interfaces.projectable_interface import ProjectableInterface
from codetocad.utilities.override import override
from providers.blender.blender_provider.blender_actions.curve import (
    is_spline_cyclical,
    loft,
)
from providers.blender.blender_provider.blender_actions.mesh import recalculate_normals
from providers.blender.blender_provider.blender_actions.normals import calculate_normal
from providers.blender.blender_provider.blender_actions.objects import get_object


class Wire(WireInterface, Entity):
    edges: "list[Edge]"
    parent_entity: Optional[str | Entity] = None
    name: str
    description: Optional[str] = None
    native_instance = None

    def __init__(
        self,
        name: "str",
        edges: "list[Edge]",
        description: "str| None" = None,
        native_instance=None,
        parent_entity: "str|Entity| None" = None,
    ):
        """
        NOTE: Blender Provider's Wire requires a parent_entity and a native_instance
        """
        assert (
            parent_entity is not None and native_instance is not None
        ), "Blender Provider's Wire requires a parent_entity and a native_instance"
        self.edges = edges
        self.parent_entity = parent_entity
        self.name = name
        self.description = description
        self.native_instance = native_instance

    @override
    def get_native_instance(self) -> object:
        return self.native_instance

    def get_normal(self, flip: "bool| None" = False) -> "Point":
        # Note: 3D surfaces will not provide a good result here.
        vertices = self.get_vertices()
        num_vertices = len(vertices)
        normal = calculate_normal(
            vertices[0].get_native_instance().co,
            vertices[int(num_vertices * 1 / 3)].get_native_instance().co,
            vertices[int(num_vertices * 2 / 3)].get_native_instance().co,
        )
        return Point.from_list_of_float_or_string(normal)

    def get_vertices(self) -> list["Vertex"]:
        if len(self.edges) == 0:
            return []
        all_vertices = [self.edges[0].v1, self.edges[0].v2]
        for edge in self.edges[1:]:
            all_vertices.append(edge.v2)
        return all_vertices

    def get_is_closed(self) -> bool:
        if not self.native_instance:
            raise Exception(
                "Cannot find native wire instance, this may mean that this reference is stale or the object does not exist in Blender."
            )
        return is_spline_cyclical(self.native_instance)

    def mirror(
        self,
        mirror_across_entity: "str|Entity",
        axis: "str|int|Axis",
        resulting_mirrored_entity_name: "str| None" = None,
    ):
        raise NotImplementedError()
        return self

    def project(self, project_from: "ProjectableInterface") -> "ProjectableInterface":
        raise NotImplementedError()
        return self

    def linear_pattern(
        self,
        instance_count: "int",
        offset: "str|float|Dimension",
        direction_axis: "str|int|Axis" = "z",
    ):
        raise NotImplementedError()
        return self

    def circular_pattern(
        self,
        instance_count: "int",
        separation_angle: "str|float|Angle",
        center_entity_or_landmark: "str|Entity",
        normal_direction_axis: "str|int|Axis" = "z",
    ):
        raise NotImplementedError()
        return self

    def loft(
        self, other: "WireInterface", new_part_name: "str| None" = None
    ) -> "PartInterface":
        blender_mesh = loft(self, other)
        part = Part(blender_mesh.name)
        if new_part_name:
            part.rename(new_part_name)
        else:
            if self.parent_entity:
                parent_name = (
                    self.parent_entity.name
                    if not isinstance(self.parent_entity, str)
                    else self.parent_entity
                )
                if type(get_object(parent_name)) == BlenderTypes.MESH.value:
                    part.union(
                        parent_name, delete_after_union=True, is_transfer_data=True
                    )
                else:
                    Entity(parent_name).delete()
                part.rename(parent_name)
            if other.parent_entity:
                parent_name = (
                    other.parent_entity.name
                    if not isinstance(other.parent_entity, str)
                    else other.parent_entity
                )
                if type(get_object(parent_name)) == BlenderTypes.MESH.value:
                    part.union(
                        parent_name, delete_after_union=True, is_transfer_data=True
                    )
                else:
                    Entity(parent_name).delete()
        recalculate_normals(part.name)
        return part

    def create_landmark(
        self,
        landmark_name: "str",
        x: "str|float|Dimension",
        y: "str|float|Dimension",
        z: "str|float|Dimension",
    ) -> "LandmarkInterface":
        print("create_landmark called", f": {landmark_name}, {x}, {y}, {z}")
        return Landmark("name", "parent")

    def get_landmark(self, landmark_name: "str|PresetLandmark") -> "LandmarkInterface":
        print("get_landmark called", f": {landmark_name}")
        return Landmark("name", "parent")

    def union(
        self,
        other: "str|Booleanable",
        delete_after_union: "bool" = True,
        is_transfer_data: "bool" = False,
    ):
        print("union called", f": {other}, {delete_after_union}, {is_transfer_data}")
        return self

    def subtract(
        self,
        other: "str|Booleanable",
        delete_after_subtract: "bool" = True,
        is_transfer_data: "bool" = False,
    ):
        print(
            "subtract called", f": {other}, {delete_after_subtract}, {is_transfer_data}"
        )
        return self

    def intersect(
        self,
        other: "str|Booleanable",
        delete_after_intersect: "bool" = True,
        is_transfer_data: "bool" = False,
    ):
        print(
            "intersect called",
            f": {other}, {delete_after_intersect}, {is_transfer_data}",
        )
        return self
