import bpy
from providers.blender.blender_provider.blender_actions.collections import (
    assign_object_to_collection,
)

from providers.blender.blender_provider.blender_actions.objects import create_object


def create_light(obj_name: str, energy_level, type):
    light_data = bpy.data.lights.new(name=obj_name, type=type)
    setattr(light_data, "energy", energy_level)
    create_object(obj_name, data=light_data)
    assign_object_to_collection(obj_name)


def get_light(
    light_name: str,
):
    blender_light = bpy.data.lights.get(light_name)

    assert blender_light is not None, f"Light {light_name} does not exist."

    return blender_light


def set_light_color(light_name: str, r_value, g_value, b_value):
    if isinstance(r_value, int):
        r_value /= 255.0

    if isinstance(g_value, int):
        g_value /= 255.0

    if isinstance(b_value, int):
        b_value /= 255.0

    light = get_light(light_name)

    light.color = (r_value, g_value, b_value)

    return light
