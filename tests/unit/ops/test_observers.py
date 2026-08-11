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

"""Unit tests for the ``observers`` module."""

import re
from dataclasses import dataclass
from typing import Annotated, Any, Literal

import ops
import pytest
from ops import testing
from pydantic import BaseModel, Field

from charmed_hpc_libs.ops import ConfigObserver, refresh


class MockCharm(ops.CharmBase):
    """Mock charm to test :class:``Observer`` classes."""

    def __init__(self, framework: ops.Framework) -> None:
        super().__init__(framework)

        self.lifecycle_observer = LifecycleObserver(self, self._config_cls)  # type: ignore
        # `self._config_class` is dynamically defined in the `mock_charm` fixture
        # using the `type` built-in. The private attribute definition is handled this way
        # to reduce the amount of scaffolding required for testing `ConfigObserver`
        # with both native Python dataclasses and pydantic data(classes/models).


class LifecycleObserver(ConfigObserver):
    """Lifecycle event observer that inherits from :class:``ConfigObserver``."""

    def __init__(self, charm: "MockCharm", config_cls: Any) -> None:
        super().__init__(charm, config_cls)

        self.charm.framework.observe(self.charm.on.config_changed, self._on_config_changed)

    @refresh(hook=None)
    def _on_config_changed(self, _: ops.ConfigChangedEvent) -> None:
        """Handle when the charm's configuration is updated with ``juju config``."""
        self.load()


@dataclass(frozen=True)
class DataclassConfigData:
    """Mock dataclass for charm application configuration data."""

    port: int

    def __post_init__(self) -> None:  # noqa D105
        # Dataclasses must provide explicit validation steps and raise `ValueError`.
        # The `load_config` method from `ops` doesn't provide any validation utilities for
        # native Python dataclasses.
        if not (1 <= self.port <= 65535):
            raise ValueError(f"port must be in range, got {self.port}")


class PydanticConfigData(BaseModel):
    """Mock pydantic model for charm application configuration data."""

    port: Literal[22] | Annotated[int, Field(ge=1024, le=65535)]


@pytest.fixture(
    scope="function",
    params=(
        pytest.param(DataclassConfigData, id="native dataclass"),
        pytest.param(PydanticConfigData, id="pydantic"),
    ),
)
def mock_charm(request: pytest.FixtureRequest) -> testing.Context[MockCharm]:
    """Mock charm context for testing :class:``Observer`` classes."""
    return testing.Context(
        type("Charm", (MockCharm,), {"_config_cls": request.param}),
        meta={"name": "test-observer-charm"},
        config={"options": {"port": {"type": "int"}}},
    )


class TestConfigObserver:
    """Test the :class:``ConfigObserver`` class."""

    @pytest.mark.parametrize(
        "mock_config,expected_status",
        (
            pytest.param({"port": 22}, ops.UnknownStatus(), id="valid config"),
            pytest.param({"port": -127}, ops.BlockedStatus(), id="invalid config"),
        ),
    )
    def test_load(
        self,
        mock_charm: testing.Context[MockCharm],
        mock_config: dict[str, Any],
        expected_status: ops.StatusBase,
    ) -> None:
        """Test the :meth:``load`` method when the application configuration is valid."""
        state = mock_charm.run(
            mock_charm.on.config_changed(), state=testing.State(config=mock_config)
        )
        assert isinstance(state.unit_status, type(expected_status))
        if isinstance(expected_status, ops.BlockedStatus):
            assert re.match(
                r"Configuration option\(s\).*\. See `juju debug-log` for details",
                state.unit_status.message,
            )
