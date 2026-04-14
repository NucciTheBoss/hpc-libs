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

"""Tests for the `exporters` library."""

from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from charmed_hpc_libs.errors import SnapError
from charmed_hpc_libs.ops import NodeExporterManager


@pytest.fixture(scope="function")
def mock_snap(mocker: MockerFixture) -> Mock:
    """Create a mocked `snap` function."""
    return mocker.patch("charmed_hpc_libs.ops.machine.snap.snap")


class TestNodeExporterManager:
    """Test the `NodeExporterManager` class."""

    @pytest.fixture
    def node_exporter_manager(self) -> NodeExporterManager:
        """Create a `NodeExporterManager` object."""
        return NodeExporterManager()

    def test_collectors(self, node_exporter_manager, mock_snap) -> None:
        """Test the `collectors` property."""
        mock_snap.return_value = ('{"collectors": "ntp cpu"}', 0)
        assert node_exporter_manager.collectors == ["ntp", "cpu"]

        node_exporter_manager.collectors = ["ntp", "cpu"]
        mock_snap.assert_called_with("set", "node-exporter", 'collectors="ntp cpu"')

        node_exporter_manager.collectors = []
        mock_snap.assert_called_with("unset", "node-exporter", "collectors")

        mock_snap.side_effect = SnapError(
            "error: snap 'node-exporter' has no 'collectors' configuration option"
        )
        assert node_exporter_manager.collectors == []

    def test_no_collectors(self, node_exporter_manager, mock_snap) -> None:
        """Test the `no_collectors` property."""
        mock_snap.return_value = ('{"no-collectors": "mdadm netstat"}', 0)
        assert node_exporter_manager.no_collectors == ["mdadm", "netstat"]

        node_exporter_manager.no_collectors = ["netstat", "btrfs"]
        mock_snap.assert_called_with("set", "node-exporter", 'no-collectors="netstat btrfs"')

        node_exporter_manager.no_collectors = []
        mock_snap.assert_called_with("unset", "node-exporter", "no-collectors")

        mock_snap.side_effect = SnapError(
            "error: snap 'node-exporter' has no 'no-collectors' configuration option"
        )
        assert node_exporter_manager.no_collectors == []

    def test_web_listen_address(self, node_exporter_manager, mock_snap) -> None:
        """Test the `web_listen_address` property."""
        mock_snap.return_value = ('{"web.listen-address": "127.0.0.1:9200"}', 0)
        assert node_exporter_manager.web_listen_address == "127.0.0.1:9200"

        node_exporter_manager.web_listen_address = "127.0.0.1:9200"
        mock_snap.assert_called_with("set", "node-exporter", 'web.listen-address="127.0.0.1:9200"')

        del node_exporter_manager.web_listen_address
        mock_snap.assert_called_with("unset", "node-exporter", "web.listen-address")

        mock_snap.side_effect = SnapError(
            "error: snap 'node-exporter' has no 'web.listen-address' configuration option"
        )
        assert node_exporter_manager.web_listen_address == ""
