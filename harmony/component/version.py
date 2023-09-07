class SemanticVersion:
    def __init__(self, sem_version):
        self._raw = sem_version

        versions = self._raw.lower().replace("v", "").split(".")

        self._major_version = int(versions[0])
        self._minor_version = int(versions[1])
        self._patch_version = int(versions[2])

        self._version = f"{self._major_version}.{self._minor_version}.{self._patch_version}"

    def __str__(self):
        return self.version

    def __repr__(self):
        return self.version

    def __hash__(self):
        return hash(self.version)

    @property
    def version(self):
        return self._version

    def compare(self, other):
        is_major_equal = True
        is_minor_equal = True
        is_patch_equal = True

        if self._major_version != other._major_version:
            is_major_equal = False

        if self._minor_version != other._minor_version:
            is_minor_equal = False

        if self._patch_version != other._patch_version:
            is_patch_equal = False

        return is_major_equal, is_minor_equal, is_patch_equal

    def get_newer_version(self, other):
        is_major_equal, is_minor_equal, is_patch_equal = self.compare(other)

        newer_version = other

        if not is_major_equal and self._major_version > other._major_version:
            newer_version = self
        elif not is_minor_equal and self._minor_version > other._minor_version:
            newer_version = self
        elif not is_patch_equal and self._patch_version > other._patch_version:
            newer_version = self

        return newer_version, newer_version.version

    def __gt__(self, other):
        _, version_string = self.get_newer_version(other)

        if version_string == other.version:
            return False

        return True

    def __eq__(self, other):
        is_major_equal, is_minor_equal, is_patch_equal = self.compare(other)
        return is_major_equal and is_minor_equal and is_patch_equal

    def get_latest_version(self, versions):
        latest_version = self
        for version in versions:
            latest_version, _ = latest_version.get_newer_version(version)

        return latest_version
