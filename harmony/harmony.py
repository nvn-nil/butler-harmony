import os
import re
import shutil
from datetime import datetime

import yaml
from yaml import SafeLoader

from harmony.component.version import SemanticVersion

CONFIG_FILE_EXT = "yaml"


def strip_semver(filename):
    semver_pattern = r"\d+\.\d+\.\d+"
    semver_regex = re.compile(semver_pattern)
    semver_match = semver_regex.search(filename)
    if semver_match:
        semver = semver_match.group()
        return semver
    else:
        return None


class Harmony:
    def __init__(self, config_dir="."):
        self.config_dir = config_dir
        self._configs = {}
        self._pending_updates = {}

        if not os.path.isdir(config_dir):
            raise Exception(f"config_dir must be a directory. Got {config_dir}")

        self.load_tool_configs()

    def load_tool_configs(self):
        for file in os.listdir(self.config_dir):
            if file.endswith(".yaml") or file.endswith(".yml"):
                filepath = os.path.join(self.config_dir, file)
                with open(filepath) as fi:
                    file_config = yaml.load(fi, SafeLoader)
                    id = file_config["id"]
                    if id not in self._configs:
                        self._configs[id] = file_config
                    else:
                        raise Exception(
                            f"Tools cannot have duplicate id: {id}]\n\t Tool {self._configs[id]['name']} has same id"
                        )

    def register_tool(
        self,
        id,
        name,
        description,
        current_version,
        location,
        name_format,
        last_updated,
        type,
        update_location,
        update_frequency,
        archive_location,
    ):
        # Create the tool configuration dictionary
        tool_config = {
            "id": id,
            "name": name,
            "description": description,
            "current_version": SemanticVersion(current_version).version,
            "location": os.path.abspath(location),
            "name_format": name_format,
            "type": type,
            "update_location": update_location,
            "update_frequency": update_frequency,
            "archive_location": archive_location,
            "last_updated": last_updated.strftime("%Y-%m-%d %H:%M")
            if last_updated
            else datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

        # Save the tool configuration to a YAML file
        self.save_tool_config(tool_config)

    def save_tool_config(self, tool_config):
        filename = os.path.join(self.config_dir, tool_config["tool_name"] + CONFIG_FILE_EXT)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "w") as f:
            yaml.safe_dump(tool_config, f)

    def current(self, tool_id):
        tool_config = self._configs[tool_id]
        name_format = tool_config["name_format"]
        location = tool_config["location"]

        assert "major" in name_format
        assert "minor" in name_format
        assert "patch" in name_format

        regex_format = name_format.replace("{major}", r"\d+").replace("{minor}", r"\d+").replace("{patch}", r"\d+")
        name_pattern = re.compile(regex_format)

        for file in os.listdir(location):
            filename_match = name_pattern.search(file)
            if filename_match:
                semver = strip_semver(file)
                return file, semver, name_pattern

        raise Exception(f"Tool not found in tool location. Location: {location} name_format: {name_format}")

    def check_update(self, id):
        config = self._configs[id]
        filename, semver, name_pattern = self.current(id)

        current_semver = SemanticVersion(semver)

        update_location = config["update_location"]

        if os.path.isdir(update_location):
            versions = []
            filenames = {}
            for file in os.listdir(update_location):
                filename_match = name_pattern.search(file)
                if filename_match:
                    semver = SemanticVersion(strip_semver(file))

                versions.append(semver)
                filenames[semver] = file

            if not versions:
                return False

            latest_semver = current_semver.get_latest_version(versions)

            if latest_semver == current_semver:
                return False
            elif latest_semver > current_semver:
                self._pending_updates[id] = [latest_semver, filenames[latest_semver]]
                return True

        raise NotImplementedError()

    def update(self, id):
        update = self.check_update(id)

        if update:
            config = self._configs[id]
            type = config["type"]
            location = config["location"]
            archive_location = config["archive_location"]
            update_location = config["update_location"]

            if os.path.isdir(update_location):
                latest_version, new_version_filename = self._pending_updates[id]

                if type == "binary":
                    try:
                        current_filename, semver, name_pattern = self.current(id)
                        current_filepath = os.path.join(location, current_filename)
                        archived_filepath = os.path.join(archive_location, current_filename)
                        shutil.move(current_filepath, archived_filepath)
                    except Exception:
                        return False
                    else:
                        try:
                            latest_filepath_src = os.path.join(update_location, new_version_filename)
                            latest_filepath_dst = os.path.join(location, new_version_filename)
                            shutil.copy2(latest_filepath_src, latest_filepath_dst)
                        except Exception:
                            shutil.move(archived_filepath, current_filepath)  # rollback
                            return False
                        else:
                            return True

            raise NotImplementedError()
