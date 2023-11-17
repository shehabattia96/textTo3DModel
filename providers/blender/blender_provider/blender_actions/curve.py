from typing import Optional
import bpy
from codetocad.codetocad_types import (
    DimensionOrItsFloatOrStringValue,
)
from codetocad.core.angle import Angle
from codetocad.core.dimension import Dimension
from .. import blender_definitions

from . import get_object, create_object, convert_object_using_ops, assign_object_to_collection, enable_curve_extra_objects_addon

from codetocad import get_dimension_list_from_string_list


def get_curve(curve_name: str) -> bpy.types.Curve:
    curve = bpy.data.curves.get(curve_name)

    assert curve is not None, f"Curve {curve_name} does not exists"

    return curve


def extrude_curve(curve_name: str, length: Dimension):
    curve = get_curve(curve_name)

    length = blender_definitions.BlenderLength.convert_dimension_to_blender_unit(
        length)

    curve.extrude = length.value


def offset_curve_geometry(curve_name: str, offset: Dimension):
    curve = get_curve(curve_name)

    length = blender_definitions.BlenderLength.convert_dimension_to_blender_unit(
        offset)

    curve.offset = length.value


def set_curve_resolution_u(curve_name: str, resolution: int):
    curve = get_curve(curve_name)

    curve.resolution_u = resolution


def set_curve_resolution_v(curve_name: str, resolution: int):
    curve = get_curve(curve_name)

    curve.resolution_v = resolution


def create_text(
    curve_name: str,
    text: str,
    size=Dimension(1),
    bold=False,
    italic=False,
    underlined=False,
    character_spacing=1,
    word_spacing=1,
    line_spacing=1,
    font_file_path: Optional[str] = None,
):
    curveData = bpy.data.curves.new(type="FONT", name=curve_name)

    setattr(curveData, "body", text)
    setattr(
        curveData,
        "size",
        blender_definitions.BlenderLength.convert_dimension_to_blender_unit(
            size).value,
    )
    setattr(curveData, "space_character", character_spacing)
    setattr(curveData, "space_word", word_spacing)
    setattr(curveData, "space_line", line_spacing)

    if font_file_path:
        fontData = bpy.data.fonts.load(font_file_path.replace("\\", "/"))
        setattr(curveData, "font", fontData)

    if bold or italic or underlined:
        curveDataBodyFormat = curveData.body_format
        for index in range(len(text)):
            curveDataBodyFormat[index].use_underline = underlined
            curveDataBodyFormat[index].use_bold = bold
            curveDataBodyFormat[index].use_italic = italic

        # setattr(curveData, "body_format", curveDataBodyFormat)

    create_object(curve_name, curveData)

    assign_object_to_collection(curve_name)

    # issue-160: scaling doesn't work well for TextCurves, so we'll convert it to a normal Curve.
    convert_object_using_ops(
        curve_name, blender_definitions.BlenderTypes.CURVE)

    curveData.use_path = False


def create_3d_curve(
    curve_name: str,
    curve_type: blender_definitions.BlenderCurveTypes,
    coordinates,
    interpolation=64,
    is_3d=False,
):
    curveData = bpy.data.curves.new(curve_name, type="CURVE")
    curveData.dimensions = "3D" if is_3d else "2D"
    curveData.resolution_u = interpolation
    curveData.use_path = False

    create_spline(curveData, curve_type, coordinates)

    create_object(curve_name, curveData)

    assign_object_to_collection(curve_name)


# Creates a new Splines instance in the bpy.types.curves object passed in as blender_curve
# then assigns the coordinates to them.
# references https://blender.stackexchange.com/a/6751/138679
def create_spline(
    blender_curve: bpy.types.Curve,
    curve_type: blender_definitions.BlenderCurveTypes,
    coordinates,
):
    coordinates = [
        blender_definitions.BlenderLength.convert_dimensions_to_blender_unit(
            get_dimension_list_from_string_list(coordinate) or []
        )
        for coordinate in coordinates
    ]
    coordinates = [
        [dimension.value for dimension in coordinate] for coordinate in coordinates
    ]

    spline = blender_curve.splines.new(curve_type.name)
    spline.order_u = 2

    # subtract 1 so the end and origin points are not connected
    number_of_points = len(coordinates) - 1

    if curve_type == blender_definitions.BlenderCurveTypes.BEZIER:
        # subtract 1 so the end and origin points are not connected
        spline.bezier_points.add(number_of_points)
        for i, coord in enumerate(coordinates):
            x, y, z = coord
            spline.bezier_points[i].co = (x, y, z)
            spline.bezier_points[i].handle_left = (x, y, z)
            spline.bezier_points[i].handle_right = (x, y, z)

    else:
        # subtract 1 so the end and origin points are not connected
        spline.points.add(number_of_points)

        for i, coord in enumerate(coordinates):
            x, y, z = coord
            spline.points[i].co = (x, y, z, 1)


def add_bevel_object_to_curve(
    path_curve_object_name: str, profile_curve_object_name: str, fill_cap=False
):
    '''
    Effectively sweeps an object along a path
    '''
    pathCurveObject = get_object(path_curve_object_name)

    profileCurveObject = get_object(profile_curve_object_name)

    assert isinstance(
        profileCurveObject.data, bpy.types.Curve
    ), f"Profile Object {profile_curve_object_name} is not a Curve object. Please use a Curve object."

    curve: bpy.types.Curve = pathCurveObject.data

    curve.bevel_mode = "OBJECT"
    curve.bevel_object = profileCurveObject
    curve.use_fill_caps = fill_cap


def get_blender_curve_primitive_function(
    curve_primitive: blender_definitions.BlenderCurvePrimitiveTypes,
):
    if curve_primitive == blender_definitions.BlenderCurvePrimitiveTypes.Point:
        return BlenderCurvePrimitives.create_point
    elif curve_primitive == blender_definitions.BlenderCurvePrimitiveTypes.LineTo:
        return BlenderCurvePrimitives.create_line_to
    elif curve_primitive == blender_definitions.BlenderCurvePrimitiveTypes.Distance:
        return BlenderCurvePrimitives.create_line
    elif curve_primitive == blender_definitions.BlenderCurvePrimitiveTypes.Angle:
        return BlenderCurvePrimitives.create_angle
    elif curve_primitive == blender_definitions.BlenderCurvePrimitiveTypes.Circle:
        return BlenderCurvePrimitives.create_circle
    elif curve_primitive == blender_definitions.BlenderCurvePrimitiveTypes.Ellipse:
        return BlenderCurvePrimitives.create_ellipse
    elif curve_primitive == blender_definitions.BlenderCurvePrimitiveTypes.Sector:
        return BlenderCurvePrimitives.create_sector
    elif curve_primitive == blender_definitions.BlenderCurvePrimitiveTypes.Segment:
        return BlenderCurvePrimitives.create_segment
    elif curve_primitive == blender_definitions.BlenderCurvePrimitiveTypes.Rectangle:
        return BlenderCurvePrimitives.create_rectangle
    elif curve_primitive == blender_definitions.BlenderCurvePrimitiveTypes.Rhomb:
        return BlenderCurvePrimitives.create_rhomb
    elif curve_primitive == blender_definitions.BlenderCurvePrimitiveTypes.Trapezoid:
        return BlenderCurvePrimitives.create_trapezoid
    elif curve_primitive == blender_definitions.BlenderCurvePrimitiveTypes.Polygon:
        return BlenderCurvePrimitives.create_polygon
    elif curve_primitive == blender_definitions.BlenderCurvePrimitiveTypes.Polygon_ab:
        return BlenderCurvePrimitives.create_polygon_ab
    elif curve_primitive == blender_definitions.BlenderCurvePrimitiveTypes.Arc:
        return BlenderCurvePrimitives.create_arc
    elif curve_primitive == blender_definitions.BlenderCurvePrimitiveTypes.Spiral:
        return BlenderCurvePrimitives.create_spiral

    raise TypeError("Unknown primitive")


class BlenderCurvePrimitives:
    @staticmethod
    def create_point(curve_type=blender_definitions.BlenderCurveTypes.NURBS, **kwargs):
        create_simple_curve(
            blender_definitions.BlenderCurvePrimitiveTypes.Point,
            use_cyclic_u=False,
            **kwargs,
        )

    @staticmethod
    def create_line_to(end_location, **kwargs):
        create_simple_curve(
            blender_definitions.BlenderCurvePrimitiveTypes.LineTo,
            Simple_endlocation=blender_definitions.BlenderLength.convert_dimension_to_blender_unit(
                Dimension.from_string(end_location)
            ).value,
            use_cyclic_u=False,
            **kwargs,
        )

    @staticmethod
    def create_line(length, **kwargs):
        create_simple_curve(
            blender_definitions.BlenderCurvePrimitiveTypes.Distance,
            Simple_length=blender_definitions.BlenderLength.convert_dimension_to_blender_unit(
                Dimension.from_string(length)
            ).value,
            Simple_center=True,
            use_cyclic_u=False,
            **kwargs,
        )

    @staticmethod
    def create_angle(length, angle, **kwargs):
        create_simple_curve(
            blender_definitions.BlenderCurvePrimitiveTypes.Angle,
            Simple_length=blender_definitions.BlenderLength.convert_dimension_to_blender_unit(
                Dimension.from_string(length)
            ).value,
            Simple_angle=Angle.from_string(angle).to_degrees().value,
            use_cyclic_u=False,
            **kwargs,
        )

    @staticmethod
    def create_circle(radius, **kwargs):
        create_simple_curve(
            blender_definitions.BlenderCurvePrimitiveTypes.Circle,
            Simple_radius=blender_definitions.BlenderLength.convert_dimension_to_blender_unit(
                Dimension.from_string(radius)
            ).value,
            Simple_sides=64,
            **kwargs,
        )

    @staticmethod
    def create_ellipse(radius_x, radius_y, **kwargs):
        create_simple_curve(
            blender_definitions.BlenderCurvePrimitiveTypes.Ellipse,
            Simple_a=blender_definitions.BlenderLength.convert_dimension_to_blender_unit(
                Dimension.from_string(radius_x)
            ).value,
            Simple_b=blender_definitions.BlenderLength.convert_dimension_to_blender_unit(
                Dimension.from_string(radius_y)
            ).value,
            **kwargs,
        )

    @staticmethod
    def create_arc(radius, angle, **kwargs):
        create_simple_curve(
            blender_definitions.BlenderCurvePrimitiveTypes.Arc,
            Simple_sides=64,
            Simple_radius=blender_definitions.BlenderLength.convert_dimension_to_blender_unit(
                Dimension.from_string(radius)
            ).value,
            Simple_startangle=0,
            Simple_endangle=Angle.from_string(angle).to_degrees().value,
            use_cyclic_u=False,
            **kwargs,
        )

    @staticmethod
    def create_sector(radius, angle, **kwargs):
        create_simple_curve(
            blender_definitions.BlenderCurvePrimitiveTypes.Sector,
            Simple_sides=64,
            Simple_radius=blender_definitions.BlenderLength.convert_dimension_to_blender_unit(
                Dimension.from_string(radius)
            ).value,
            Simple_startangle=0,
            Simple_endangle=Angle.from_string(angle).to_degrees().value,
            **kwargs,
        )

    @staticmethod
    def create_segment(outter_radius, inner_radius, angle, **kwargs):
        create_simple_curve(
            blender_definitions.BlenderCurvePrimitiveTypes.Segment,
            Simple_sides=64,
            Simple_a=blender_definitions.BlenderLength.convert_dimension_to_blender_unit(
                Dimension.from_string(outter_radius)
            ).value,
            Simple_b=blender_definitions.BlenderLength.convert_dimension_to_blender_unit(
                Dimension.from_string(inner_radius)
            ).value,
            Simple_startangle=0,
            Simple_endangle=Angle.from_string(angle).to_degrees().value,
            **kwargs,
        )

    @staticmethod
    def create_rectangle(length, width, **kwargs):
        create_simple_curve(
            blender_definitions.BlenderCurvePrimitiveTypes.Rectangle,
            Simple_length=blender_definitions.BlenderLength.convert_dimension_to_blender_unit(
                Dimension.from_string(length)
            ).value,
            Simple_width=blender_definitions.BlenderLength.convert_dimension_to_blender_unit(
                Dimension.from_string(width)
            ).value,
            Simple_rounded=0,
            **kwargs,
        )

    @staticmethod
    def create_rhomb(length, width, **kwargs):
        create_simple_curve(
            blender_definitions.BlenderCurvePrimitiveTypes.Rhomb,
            Simple_length=blender_definitions.BlenderLength.convert_dimension_to_blender_unit(
                Dimension.from_string(length)
            ).value,
            Simple_width=blender_definitions.BlenderLength.convert_dimension_to_blender_unit(
                Dimension.from_string(width)
            ).value,
            Simple_center=True,
            **kwargs,
        )

    @staticmethod
    def create_polygon(number_of_sides, radius, **kwargs):
        create_simple_curve(
            blender_definitions.BlenderCurvePrimitiveTypes.Polygon,
            Simple_sides=number_of_sides,
            Simple_radius=blender_definitions.BlenderLength.convert_dimension_to_blender_unit(
                Dimension.from_string(radius)
            ).value,
            **kwargs,
        )

    @staticmethod
    def create_polygon_ab(number_of_sides, length, width, **kwargs):
        create_simple_curve(
            blender_definitions.BlenderCurvePrimitiveTypes.Polygon_ab,
            Simple_sides=number_of_sides,
            Simple_a=blender_definitions.BlenderLength.convert_dimension_to_blender_unit(
                Dimension.from_string(length)
            ).value,
            Simple_b=blender_definitions.BlenderLength.convert_dimension_to_blender_unit(
                Dimension.from_string(width)
            ).value,
            **kwargs,
        )

    @staticmethod
    def create_trapezoid(length_upper, length_lower, height, **kwargs):
        create_simple_curve(
            blender_definitions.BlenderCurvePrimitiveTypes.Trapezoid,
            Simple_a=blender_definitions.BlenderLength.convert_dimension_to_blender_unit(
                Dimension.from_string(length_upper)
            ).value,
            Simple_b=blender_definitions.BlenderLength.convert_dimension_to_blender_unit(
                Dimension.from_string(length_lower)
            ).value,
            Simple_h=blender_definitions.BlenderLength.convert_dimension_to_blender_unit(
                Dimension.from_string(height)
            ).value,
            **kwargs,
        )

    @staticmethod
    def create_spiral(
        number_of_turns: "int",
        height: DimensionOrItsFloatOrStringValue,
        radius: DimensionOrItsFloatOrStringValue,
        is_clockwise: bool = True,
        radius_end: Optional[DimensionOrItsFloatOrStringValue] = None,
        **kwargs,
    ):
        enable_curve_extra_objects_addon()

        heightMeters = (
            blender_definitions.BlenderLength.convert_dimension_to_blender_unit(
                Dimension.from_string(height)
            ).value
        )

        radiusMeters = (
            blender_definitions.BlenderLength.convert_dimension_to_blender_unit(
                Dimension.from_string(radius)
            ).value
        )

        radius_endMeters = (
            blender_definitions.BlenderLength.convert_dimension_to_blender_unit(
                Dimension.from_string(radius_end)
            )
            if radius_end
            else None
        )

        radiusDiff = (
            0 if radius_endMeters is None else (
                radius_endMeters - radiusMeters).value
        )

        curve_type: blender_definitions.BlenderCurveTypes = (
            kwargs["curve_type"]
            if "curve_type" in kwargs and kwargs["curve_type"]
            else blender_definitions.BlenderCurvePrimitiveTypes.Spiral.get_default_curve_type()
        )

        curve_typeName: str = curve_type.name

        bpy.ops.curve.spirals(
            spiral_type="ARCH",
            turns=number_of_turns,
            steps=24,
            edit_mode=False,
            radius=radiusMeters,
            dif_z=heightMeters / number_of_turns,
            dif_radius=radiusDiff,
            curve_type=curve_typeName,
            spiral_direction="CLOCKWISE" if is_clockwise else "COUNTER_CLOCKWISE",
        )


# assumes add_curve_extra_objects is enabled
# https://github.com/blender/blender-addons/blob/master/add_curve_extra_objects/add_curve_simple.py
def create_simple_curve(
    curve_primitiveType: blender_definitions.BlenderCurvePrimitiveTypes, **kwargs
):
    curve_type: blender_definitions.BlenderCurveTypes = (
        kwargs["curve_type"]
        if "curve_type" in kwargs and kwargs["curve_type"]
        else curve_primitiveType.get_default_curve_type()
    )

    kwargs.pop("curve_type", None)  # remove curve_type from kwargs

    enable_curve_extra_objects_addon()

    assert isinstance(
        curve_primitiveType, blender_definitions.BlenderCurvePrimitiveTypes
    ), "{} is not a known curve primitive. Options: {}".format(
        curve_primitiveType,
        [b.name for b in blender_definitions.BlenderCurvePrimitiveTypes],
    )

    assert isinstance(
        curve_type, blender_definitions.BlenderCurveTypes
    ), "{} is not a known simple curve type. Options: {}".format(
        curve_type, [b.name for b in blender_definitions.BlenderCurveTypes]
    )

    # Make sure an object or curve with the same name don't already exist:
    blenderObject = bpy.data.objects.get(curve_primitiveType.name)
    blender_curve = bpy.data.curves.get(curve_primitiveType.name)

    assert (
        blenderObject is None
    ), f"An object with name {curve_primitiveType.name} already exists."
    assert (
        blender_curve is None
    ), f"A curve with name {curve_primitiveType.name} already exists."

    # Default values:
    # bpy.ops.curve.simple(align='WORLD', location=(0, 0, 0), rotation=(0, 0, 0), Simple=True, Simple_Change=False, Simple_Delete="", Simple_Type='Point', Simple_endlocation=(2, 2, 2), Simple_a=2, Simple_b=1, Simple_h=1, Simple_angle=45, Simple_startangle=0, Simple_endangle=45, Simple_sides=3, Simple_radius=1, Simple_center=True, Simple_degrees_or_radians='Degrees', Simple_width=2, Simple_length=2, Simple_rounded=0, shape='2D', outputType='BEZIER', use_cyclic_u=True, endp_u=True, order_u=4, handleType='VECTOR', edit_mode=True)
    bpy.ops.curve.simple(
        Simple_Type=curve_primitiveType.name,
        outputType=curve_type.name,
        order_u=2,
        shape="2D",
        edit_mode=False,
        **kwargs,
    )


def set_curve_use_path(curve_name: str, is_use_path: bool):
    curveObject = get_object(curve_name)

    curve: bpy.types.Curve = curveObject.data

    curve.use_path = is_use_path
