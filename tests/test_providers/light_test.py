# THIS IS AN AUTO-GENERATE FILE.
# DO NOT EDIT MANUALLY.
# Please run development/capabilities_json_to_python/capabilities_to_py.sh to generate this file.

# testsSample will implement these interfaces - this ensures that as capabilities.json is updated, tests are up to date as well.

from unittest import skip

from .test_helper import *
from codetocad.tests_interfaces import LightTestInterface


class LightTest(TestProviderCase, LightTestInterface):

    @skip("TODO")
    def test_set_color(self):
        instance = Light("name", "description")

        value = instance.set_color("r_value", "g_value", "b_value")

        assert value, "Modify method failed."

    @skip("TODO")
    def test_create_sun(self):
        instance = Light("name", "description")

        value = instance.create_sun("energy_level")

        assert value.is_exists(), "Create method failed."

    @skip("TODO")
    def test_create_spot(self):
        instance = Light("name", "description")

        value = instance.create_spot("energy_level")

        assert value.is_exists(), "Create method failed."

    @skip("TODO")
    def test_create_point(self):
        instance = Light("name", "description")

        value = instance.create_point("energy_level")

        assert value.is_exists(), "Create method failed."

    @skip("TODO")
    def test_create_area(self):
        instance = Light("name", "description")

        value = instance.create_area("energy_level")

        assert value.is_exists(), "Create method failed."

    @skip("TODO")
    def test_translate_xyz(self):
        instance = Light("name", "description")

        value = instance.translate_xyz("x", "y", "z")

        assert value, "Modify method failed."

    @skip("TODO")
    def test_rotate_xyz(self):
        instance = Light("name", "description")

        value = instance.rotate_xyz("x", "y", "z")

        assert value, "Modify method failed."

    @skip("TODO")
    def test_is_exists(self):
        instance = Light("name", "description")

        value = instance.is_exists("")

        assert value, "Get method failed."

    @skip("TODO")
    def test_rename(self):
        instance = Light("name", "description")

        value = instance.rename("new_name")

        assert value, "Modify method failed."

    @skip("TODO")
    def test_delete(self):
        instance = Light("name", "description")

        value = instance.delete("")

    @skip("TODO")
    def test_get_native_instance(self):
        instance = Light("name", "description")

        value = instance.get_native_instance("")

        assert value, "Get method failed."

    @skip("TODO")
    def test_get_location_world(self):
        instance = Light("name", "description")

        value = instance.get_location_world("")

        assert value, "Get method failed."

    @skip("TODO")
    def test_get_location_local(self):
        instance = Light("name", "description")

        value = instance.get_location_local("")

        assert value, "Get method failed."

    @skip("TODO")
    def test_select(self):
        instance = Light("name", "description")

        value = instance.select("")
