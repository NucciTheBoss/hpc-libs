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

    @property
    def collectors(self) -> list[str]:
        """Get the list of optionally-enabled collectors.

        Providing an empty list `[]` will disable all optionally-enabled collectors.

        Examples:
            >>> node_exporter = NodeExporterManager()
            >>> node_exporter.collectors = ["ntp"]
            >>> node_exporter.collectors
            >>> ["ntp"]
        """
        try:
            return self.get("collectors").split()
        except SnapError:
            # `SnapError` is raised if `collectors` option is empty.
            return []

    @collectors.setter
    def collectors(self, value: Collection[str]) -> None:
        if len(value) == 0:
            self.unset("collectors")
        else:
            self.set({"collectors": " ".join(value)})

    @property
    def no_collectors(self) -> list[str]:
        """Get the list of disabled collectors.

        Examples:
            >>> node_exporter = NodeExporterManager()
            >>> node_exporter.no_collectors = ["mdadm", "netstat"]
            >>> node_exporter.no_collectors
            >>> ["mdadm", "netstat"]
        """
        try:
            return self.get("no-collectors").split()
        except SnapError:
            # `SnapError` is raised if `no-collectors` option is empty.
            return []

    @no_collectors.setter
    def no_collectors(self, value: Collection[str]) -> None:
        if len(value) == 0:
            self.unset("no-collectors")
        else:
            self.set({"no-collectors": " ".join(value)})

    @property
    def web_listen_address(self) -> str:
        """Get web address and port used by the `node-exporter` service.

        Examples:
            >>> node_exporter = NodeExporterManager()
            >>> node_exporter.web_listen_address
            >>> ":9200"
            >>> node_exporter.web_listen_address = "127.0.0.1:9200"
            >>> node_exporter.web_listen_address
            >>> "127.0.0.1:9200"
        """
        try:
            return self.get("web.listen-address")
        except SnapError:
            # `SnapError` is raised if `web.listen-address` option is empty.
            return ""

    @web_listen_address.setter
    def web_listen_address(self, value: str) -> None:
        self.set({"web.listen-address": value})

    @web_listen_address.deleter
    def web_listen_address(self) -> None:
        self.unset("web.listen-address")
