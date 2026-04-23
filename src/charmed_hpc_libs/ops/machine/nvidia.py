# Copyright 2026 Canonical Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Manage Nvidia GPU-related devices and artifacts."""

__all__ = ["DCGMManager"]

from functools import cached_property
from pathlib import Path

from ...errors import SnapError
from .snap import SnapLifecycleManager, SnapServiceManager


class DCGMManager(SnapLifecycleManager):
    """Control the lifecycle of Nvidia's Data Center GPU Manager."""

    def __init__(self) -> None:
        super().__init__("dcgm")

    @cached_property
    def exporter(self) -> SnapServiceManager:
        """Get the service manager for the `dcgm-exporter` service."""
        return self._ops_manager.service_manager_for("dcgm-exporter")

    @cached_property
    def nv_hostengine(self) -> SnapServiceManager:
        """Get the service manager for the `nv-hostengine` service."""
        return self._ops_manager.service_manager_for("nv-hostengine")

    def get_dcgm_exporter_address(self) -> str:
        """Get the address used by the `dcgm-exporter` service.

        Notes:
            - The default address is `:9400`
            - An empty `str` object is returned if the output 'snap get -d dcgm' does not
              contain a configured address for the `dcgm-exporter` service.
        """
        try:
            return self.config.get("dcgm-exporter-address")
        except SnapError:
            # `SnapError` is raised if `dcgm-exporter-address` option is empty.
            return ""

    def set_dcgm_exporter_address(self, value: str) -> None:
        """Set the web address and port used by the `dcgm-exporter` service.

        Args:
            value: The address to use for the `dcgm-exporter` service.

        Notes:
            - Providing an empty string will unset the custom listen address.
        """
        if value:
            self.config.set({"dcgm-exporter-address": str(value)})
        else:
            self.config.unset("dcgm-exporter-address")

    def get_dcgm_exporter_metrics_file(self) -> Path | None:
        """Get the path to the custom CSV metrics file loaded by the `dcgm-exporter` service.

        Notes:
            - The default metrics file is located at
              `/snap/dcgm/current/etc/dcgm-exporter/default-counters.csv`
            - An `None` is returned if the output of 'snap get -d dcgm' does not
              contain a configured path for the metrics file.
        """
        try:
            return Path(self.config.get("dcgm-exporter-metrics-file"))
        except SnapError:
            # `SnapError` is raised if `dcgm-exporter-metrics-file` option is empty.
            return None

    def set_dcgm_exporter_metrics_file(self, value: str | Path) -> None:
        """Set the path to the custom CSV metrics file loaded by the `dcgm-exporter` service.

        Args:
            value: The path to the new custom metrics file.

        Notes:
            - Providing an empty string or `Path` object will unset the custom metrics file path.
        """
        if value == "" or value == Path():
            self.config.unset("dcgm-exporter-metrics-file")
        else:
            self.config.set({"dcgm-exporter-metrics-file": str(value)})

    def get_nv_hostengine_port(self) -> int | None:
        """Get the port that the NV-Hostengine is listening on.

        Notes:
            - The default port number is 5555.
            - `None` is returned if the output of 'snap get -d dcgm' does not
              contain a configured port for the NV-Hostengine service.
        """
        try:
            return self.config.get("nv-hostengine-port")
        except SnapError:
            # `SnapError` is raised if `nv-hostengine-port` option is empty.
            return None

    def set_nv_hostengine_port(self, value: int | None) -> None:
        """Set the port that the NV-Hostengine is listening on.

        Args:
            value: The port to use for the NV-Hostengine service.

        Notes:
            - Providing the value `None` will unset the custom port number.
        """
        if value is not None:
            self.config.set({"nv-hostengine-port": value})
        else:
            self.config.unset("nv-hostengine-port")
