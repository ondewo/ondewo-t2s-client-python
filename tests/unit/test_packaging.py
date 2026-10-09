# Copyright 2021-2026 ONDEWO GmbH
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
"""
The wheel and the sdist ship the PEP 561 ``ondewo/t2s/py.typed`` marker.

Without it a consumer's mypy treats ``ondewo.t2s`` as untyped and cannot check calls into it.
6.6.3 was published without the marker although the source tree had one, so the guard builds
the real artefacts with ``uv build`` instead of reading ``pyproject.toml``. ``ondewo`` is a
namespace package, so the marker belongs in ``ondewo/t2s/``, never in ``ondewo/``.
"""

import shutil
import subprocess
import tarfile
import zipfile
from pathlib import Path
from typing import List

import pytest

REPO_ROOT: Path = Path(__file__).resolve().parents[2]
MARKER: str = "ondewo/t2s/py.typed"


@pytest.fixture(scope="module")
def dist_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Build the sdist, then the wheel from that sdist, into a temporary directory."""
    uv = shutil.which("uv")
    assert uv is not None, "uv is required to build the distributions"
    out: Path = tmp_path_factory.mktemp("dist")
    subprocess.run([uv, "build", "--quiet", "--out-dir", str(out), str(REPO_ROOT)], check=True)
    return out


def test_the_marker_exists_in_the_source_tree() -> None:
    assert (REPO_ROOT / MARKER).is_file()
    assert not (REPO_ROOT / "ondewo" / "py.typed").exists()


def test_the_wheel_ships_the_marker(dist_dir: Path) -> None:
    wheels: List[Path] = list(dist_dir.glob("*.whl"))
    assert len(wheels) == 1
    with zipfile.ZipFile(wheels[0]) as wheel:
        assert MARKER in wheel.namelist()


def test_the_sdist_ships_the_marker(dist_dir: Path) -> None:
    sdists: List[Path] = list(dist_dir.glob("*.tar.gz"))
    assert len(sdists) == 1
    with tarfile.open(sdists[0]) as sdist:
        names: List[str] = [name.split("/", 1)[1] for name in sdist.getnames() if "/" in name]
    assert MARKER in names
