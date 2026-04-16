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

"""Manage metrics exporters in HPC charms."""

__all__ = ["NodeExporterManager"]

from collections.abc import Collection

from ..errors import SnapError
from .machine import SnapLifecycleManager


class NodeExporterManager(SnapLifecycleManager):
    """Manage the `node-exporter` metrics service."""

    def __init__(self) -> None:
        super().__init__("node-exporter")

    def get_collectors(self) -> list[str]:
        """Get the list of optionally-enabled collectors.

        Examples:
            >>> node_exporter = NodeExporterManager()
            >>> node_exporter.set_collectors(["ntp"])
            >>> node_exporter.get_collectors()
            >>> ["ntp"]
        """
        try:
            return self.get("collectors").split()
        except SnapError:
            # `SnapError` is raised if `collectors` option is empty.
            return []

    def set_collectors(self, value: Collection[str]) -> None:
        """Enable optional collectors.

        Args:
            value: Collection of optional collectors to enable.

        Notes:
            - Providing an empty collection will unset all optionally-enabled collectors.
            - The service will restart after the list of collectors is updated.
        """
        if len(value) == 0:
            self.unset("collectors")
        else:
            self.set({"collectors": " ".join(value)})

    def get_no_collectors(self) -> list[str]:
        """Get the list of disabled collectors.

        Examples:
            >>> node_exporter = NodeExporterManager()
            >>> node_exporter.set_no_collectors(["mdadm", "netstat"])
            >>> node_exporter.get_no_collectors()
            >>> ["mdadm", "netstat"]
        """
        try:
            return self.get("no-collectors").split()
        except SnapError:
            # `SnapError` is raised if `no-collectors` option is empty.
            return []

    def set_no_collectors(self, value: Collection[str]) -> None:
        """Disable collectors.

        Args:
            value: Collection of collectors to disable.

        Notes:
            - Providing an empty collection will unset all disabled collectors.
            - The service will restart after the list of disabled collectors is updated.
        """
        if len(value) == 0:
            self.unset("no-collectors")
        else:
            self.set({"no-collectors": " ".join(value)})

    def get_web_listen_address(self) -> str:
        """Get web address and port used by the `node-exporter` service.

        Examples:
            >>> node_exporter = NodeExporterManager()
            >>> node_exporter.get_web_listen_address()
            >>> ":9200"
            >>> node_exporter.set_web_listen_address("127.0.0.1:9200")
            >>> node_exporter.get_web_listen_address()
            >>> "127.0.0.1:9200"
        """
        try:
            return self.get("web.listen-address")
        except SnapError:
            # `SnapError` is raised if `web.listen-address` option is empty.
            return ""

    def set_web_listen_address(self, value: str) -> None:
        """Set web address and port used by the `node-exporter` service.

        Args:
            value: The web listen address to use for the `node-exporter` service.

        Notes:
            - Providing an empty string will unset the web listen address.
            - The service will restart after the web listen address is updated.
        """
        if value:
            self.set({"web.listen-address": value})
        else:
            self.unset("web.listen-address")
