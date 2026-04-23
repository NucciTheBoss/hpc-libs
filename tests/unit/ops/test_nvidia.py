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

"""Tests for the `nvidia` library."""

from pathlib import Path
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from charmed_hpc_libs.errors import SnapError
from charmed_hpc_libs.ops import DCGMManager


@pytest.fixture(scope="function")
def mock_snap(mocker: MockerFixture) -> Mock:
    """Create a mocked `snap` function."""
    return mocker.patch("charmed_hpc_libs.ops.machine.snap.snap")


class TestDCGMManager:
    """Test the `DCGMManager` class."""

    @pytest.fixture
    def dcgm_manager(self) -> DCGMManager:
        """Create a `DCGMManager` object."""
        return DCGMManager()

    def test_exporter_service(self, dcgm_manager, mock_snap) -> None:
        """Test the `exporter` property returns a manager for the dcgm-exporter service."""
        dcgm_manager.exporter.start()
        mock_snap.assert_called_with("start", "dcgm.dcgm-exporter")

    def test_nv_hostengine_service(self, dcgm_manager, mock_snap) -> None:
        """Test the `nv_hostengine` property returns a manager for the nv-hostengine service."""
        dcgm_manager.nv_hostengine.start()
        mock_snap.assert_called_with("start", "dcgm.nv-hostengine")

    def test_get_dcgm_exporter_address(self, dcgm_manager, mock_snap) -> None:
        """Test the `get_dcgm_exporter_address` method returns the configured address."""
        mock_snap.return_value = ('{"dcgm-exporter-address": ":9400"}', 0)
        assert dcgm_manager.get_dcgm_exporter_address() == ":9400"

        dcgm_manager.set_dcgm_exporter_address(":9401")
        mock_snap.assert_called_with("set", "dcgm", 'dcgm-exporter-address=":9401"')

        dcgm_manager.set_dcgm_exporter_address("")
        mock_snap.assert_called_with("unset", "dcgm", "dcgm-exporter-address")

        mock_snap.side_effect = SnapError(
            "error: snap 'dcgm' has no 'dcgm-exporter-address' configuration option"
        )
        assert dcgm_manager.get_dcgm_exporter_address() == ""

    def test_get_dcgm_exporter_metrics_file(self, dcgm_manager, mock_snap) -> None:
        """Test `get_dcgm_exporter_metrics_file` returns the configured metrics file path."""
        mock_snap.return_value = ('{"dcgm-exporter-metrics-file": "/etc/dcgm/custom.csv"}', 0)
        assert dcgm_manager.get_dcgm_exporter_metrics_file() == Path("/etc/dcgm/custom.csv")

        dcgm_manager.set_dcgm_exporter_metrics_file("/etc/dcgm/custom.csv")
        mock_snap.assert_called_with(
            "set", "dcgm", 'dcgm-exporter-metrics-file="/etc/dcgm/custom.csv"'
        )

        dcgm_manager.set_dcgm_exporter_metrics_file(Path("/etc/dcgm/custom.csv"))
        mock_snap.assert_called_with(
            "set", "dcgm", 'dcgm-exporter-metrics-file="/etc/dcgm/custom.csv"'
        )

        dcgm_manager.set_dcgm_exporter_metrics_file("")
        mock_snap.assert_called_with("unset", "dcgm", "dcgm-exporter-metrics-file")

        mock_snap.side_effect = SnapError(
            "error: snap 'dcgm' has no 'dcgm-exporter-metrics-file' configuration option"
        )
        assert dcgm_manager.get_dcgm_exporter_metrics_file() is None

    def test_get_nv_hostengine_port(self, dcgm_manager, mock_snap) -> None:
        """Test `get_nv_hostengine_port` returns the configured port number."""
        mock_snap.return_value = ('{"nv-hostengine-port": 5556}', 0)
        assert dcgm_manager.get_nv_hostengine_port() == 5556

        dcgm_manager.set_nv_hostengine_port(5556)
        mock_snap.assert_called_with("set", "dcgm", "nv-hostengine-port=5556")

        dcgm_manager.set_nv_hostengine_port(None)
        mock_snap.assert_called_with("unset", "dcgm", "nv-hostengine-port")

        mock_snap.side_effect = SnapError(
            "error: snap 'dcgm' has no 'nv-hostengine-port' configuration option"
        )
        assert dcgm_manager.get_nv_hostengine_port() is None
