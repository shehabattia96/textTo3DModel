import bpy

from providers.blender.blender_provider.blender_actions.objects import get_object


def update_view_layer():
    bpy.context.view_layer.update()


# Applies the dependency graph to the object and persists its data using .copy()
# This allows us to apply modifiers, UV data, etc.. to the mesh.
# This is different from apply_object_transformations()
def apply_dependency_graph(
    existing_object_name: str,
):
    blender_object = get_object(existing_object_name)
    blender_object_evaluated: bpy.types.Object = blender_object.evaluated_get(
        bpy.context.evaluated_depsgraph_get()
    )
    blender_object.data = blender_object_evaluated.data.copy()


def select_object(object_name: str):
    blender_object = get_object(object_name)

    blender_object.select_set(True)


def get_selected_object_name() -> str:
    selectedObjects = bpy.context.selected_objects

    assert len(selectedObjects) > 0, "There are no selected objects."

    return selectedObjects[0].name


def get_context_view_3d(**kwargs):
    window = bpy.context.window_manager.windows[0]
    for area in window.screen.areas:
        if area.type == "VIEW_3D":
            for region in area.regions:
                if region.type == "WINDOW":
                    return bpy.context.temp_override(
                        window=window, area=area, region=region, **kwargs
                    )
    raise Exception("Could not find a VIEW_3D region.")


def zoom_to_selected_objects():
    bpy.context.view_layer.update()
    # References https://blender.stackexchange.com/a/7419/138679
    with get_context_view_3d():
        bpy.ops.view3d.view_selected(use_all_regions=True)
        return


def add_dependency_graph_update_listener(callback):
    bpy.app.handlers.depsgraph_update_post.append(callback)


def add_timer(callback):
    bpy.app.timers.register(callback)


def get_blender_version() -> tuple:
    return bpy.app.version


def log_message(
    message: str,
):
    bpy.ops.codetocad.log_message(message=message)
