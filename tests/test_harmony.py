import os

from _base import BaseTestCase

from harmony.harmony import Harmony


class TestHarmony(BaseTestCase):
    def test_harmonize_local_artifact_location(self):
        harmony = Harmony(os.path.join(self.path, "datasets", "local_folder", "configuration"))

        # Assert tool config imported
        self.assertEquals(list(harmony._configs.keys()), ["tool"])

        filename, semver, name_pattern = harmony.current("tool")

        self.assertEqual(filename, "tool_v1.0.0.exe")
        self.assertEqual(semver, "1.0.0")

        update = harmony.check_update("tool")
        self.assertTrue(update)

        success = harmony.update("tool")
        self.assertTrue(success)
