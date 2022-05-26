# stdlib
import re
import tempfile
from typing import Iterator

# 3rd party
import platformdirs
import pytest
from consolekit.testing import CliRunner
from domdf_python_tools.paths import PathPlus, in_directory

# this package
from repo_helper_pycharm import docs_command
from repo_helper_pycharm.docs import get_config_dir, get_docs_port, open_in_browser


def re_windowspath(string: str) -> str:
	return string.replace('\\', "\\\\")


@pytest.fixture()
def mocked_config(monkeypatch) -> Iterator:
	with tempfile.TemporaryDirectory() as tmpdir:
		monkeypatch.setattr(platformdirs, "user_config_dir", lambda *args: PathPlus(tmpdir))

		example_config = PathPlus(__file__).parent / "example_config"
		tmp_configdir = PathPlus(tmpdir) / "PyCharm2020.2" / "options"
		tmp_configdir.mkdir(parents=True)

		for filename in {"other.xml", "web-browsers.xml"}:
			(tmp_configdir / filename).write_text((example_config / filename).read_text())

		yield tmpdir


def test_get_config_dir(monkeypatch, tmp_pathplus: PathPlus) -> None:
	monkeypatch.setattr(platformdirs, "user_config_dir", lambda *args: str(tmp_pathplus / "JetBrains"))

	with pytest.raises(FileNotFoundError, match=re_windowspath(f"^{tmp_pathplus / 'JetBrains'}$")):
		get_config_dir()

	(tmp_pathplus / "JetBrains").mkdir()

	with pytest.raises(
			FileNotFoundError,
			match=f"^{re.escape(str(tmp_pathplus / 'JetBrains' / 'PyCharm[0-9]{4}.[0-9]'))}$",
			):
		get_config_dir()


@pytest.mark.usefixtures("mocked_config")
def test_get_docs_port() -> None:
	assert get_docs_port() == 63333


def test_get_docs_port_missing_config(monkeypatch, tmp_pathplus: PathPlus) -> None:
	monkeypatch.setattr(platformdirs, "user_config_dir", lambda *args: str(tmp_pathplus / "JetBrains"))

	(tmp_pathplus / "JetBrains" / "PyCharm2020.2").mkdir(parents=True)
	options_dir = tmp_pathplus / "JetBrains" / "PyCharm2020.2" / "options"

	with pytest.raises(FileNotFoundError, match=re_windowspath(f"^{options_dir / 'other.xml'}$")):
		get_docs_port()

	options_dir.mkdir()

	with pytest.raises(FileNotFoundError, match=re_windowspath(f"^{options_dir / 'other.xml'}$", )):
		get_docs_port()


def test_open_in_browser_missing_config(monkeypatch, tmp_pathplus: PathPlus) -> None:
	monkeypatch.setattr(platformdirs, "user_config_dir", lambda *args: str(tmp_pathplus / "JetBrains"))

	(tmp_pathplus / "JetBrains" / "PyCharm2020.2").mkdir(parents=True)
	options_dir = tmp_pathplus / "JetBrains" / "PyCharm2020.2" / "options"

	with pytest.raises(FileNotFoundError, match=re_windowspath(f"^{options_dir / 'web-browsers.xml'}$", )):
		open_in_browser("https://google.com")

	options_dir.mkdir()

	with pytest.raises(FileNotFoundError, match=re_windowspath(f"^{options_dir / 'web-browsers.xml'}$", )):
		open_in_browser("https://google.com")


def test_has_no_docs(tmp_pathplus: PathPlus) -> None:
	(tmp_pathplus / "repo_helper.yml").write_lines([
			"modname: 'repo_helper_pycharm'",
			"copyright_years: '2020'",
			"author: 'Dominic Davis-Foster'",
			"email: 'dominic@davis-foster.co.uk'",
			"username: 'domdfcoding'",
			"version: '0.2.1'",
			"license: 'MIT'",
			"short_desc: \"repo_helper extension to manage PyCharm's configuration.\"",
			"enable_docs: False",
			])

	with in_directory(tmp_pathplus):
		runner = CliRunner(mix_stderr=False)
		result = runner.invoke(docs_command, color=False)

	assert result.exit_code == 1
	assert not result.stdout
	assert result.stderr == "The current project has no documentation!\nAborted!\n"
