import os

import requests_mock
from _base import BaseTestCase

from harmony import VersionManifest


class TestVersionManifest(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.sample_version_manifest = os.path.join(self.path, "sample_version_manifest.yaml")
        self.sample_file_link = "https://github.com/nvn-nil/company_version_manifest/versions.yaml"

    def test_get_versions_of_software(self):
        with requests_mock.mock() as mock:
            with open(self.sample_version_manifest, "rb") as fi:
                mock.get(self.sample_file_link, body=fi)

                ver = VersionManifest(self.sample_file_link)

                manifest_version = ver.version
                versions_A = ver.get_software_versions("software_A")
                versions_B = ver.get_software_versions("software_B")
                versions_C = ver.get_software_versions("software_C")

                self.assertEqual(manifest_version, 1)
                self.assertEqual(versions_A, ["0.0.1"])
                self.assertEqual(versions_B, ["0.0.1", "0.0.2"])
                self.assertEqual(versions_C, ["0.0.1", "0.0.3", "0.0.2"])

    def test_compare_versions_all_equal(self):
        with requests_mock.mock() as mock:
            with open(self.sample_version_manifest, "rb") as fi:
                mock.get(self.sample_file_link, body=fi)

                ver = VersionManifest(self.sample_file_link)
                equal, major_difference, minor_difference, patch_difference = ver.compare_version(ver)

                self.assertEqual(equal, list(ver.list_software().keys()))
                self.assertEqual(major_difference, [])
                self.assertEqual(minor_difference, [])
                self.assertEqual(patch_difference, [])

                res = ver.get_latest_version("software_A")
                self.assertEqual(res, "0.0.1")

                res = ver.get_latest_version("software_B")
                self.assertEqual(res, "0.0.2")

                res = ver.get_latest_version("software_C")
                self.assertEqual(res, "0.0.3")
