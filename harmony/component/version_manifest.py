from functools import reduce

import requests
import yaml

from .version import SemanticVersion


class ManifestLoader:
    def __init__(self):
        pass

    def load(self, content):
        self._raw = content
        self._raw_loaded = yaml.safe_load(content)
        self.version = self._raw_loaded.get("manifest_version")

        def broken_loader(*args):
            raise NotImplementedError(f"Loader for version '{self.version}' not implemented")

        loader = getattr(self, f"load_version_{self.version}", broken_loader)
        return loader(content)

    def load_version_1(self, content):
        return yaml.safe_load(content)


class VersionManifest:
    def __init__(self, url):
        self._url = url

        self._req = requests.get(self._url)
        assert self._req.status_code == 200

        loader = ManifestLoader()
        self._content = loader.load(self._req.text)
        self._version = loader.version

    def list_software(self):
        return self.content["softwares"]

    def get_software_versions(self, software_name):
        return self.content["softwares"].get(software_name, [])

    def get_latest_version(self, software_name):
        list_of_versions = self.get_software_versions(software_name)
        return reduce(lambda x, y: x if SemanticVersion(x) >= SemanticVersion(y) else y, list_of_versions)

    @property
    def content(self):
        return self._content

    @property
    def version(self):
        return self._version

    def compare_version(self, version_manifest):
        major_difference = []
        minor_difference = []
        patch_difference = []
        equal = []
        if isinstance(version_manifest, VersionManifest):
            for software in self.list_software():
                if software in version_manifest.list_software():
                    this_version = SemanticVersion(self.get_software_versions(software)[-1])
                    other_version = SemanticVersion(version_manifest.get_software_versions(software)[-1])
                    is_major_equal, is_minor_equal, is_patch_equal = this_version.compare(other_version)
                    if not is_major_equal:
                        major_difference.append(software)

                    elif not is_minor_equal:
                        minor_difference.append(software)

                    elif not is_patch_equal:
                        patch_difference.append(software)
                    else:
                        equal.append(software)

        return equal, major_difference, minor_difference, patch_difference
