# stdlib
import re
import tempfile

# 3rd party
import appdirs  # type: ignore
import pytest
from domdf_python_tools.paths import PathPlus

# this package
from repo_helper_pycharm.docs import get_config_dir, get_docs_port, open_in_browser


def re_windowspath(string: str) -> str:
	return string.replace('\\', "\\\\")


@pytest.fixture()
def mocked_config(monkeypatch):
	with tempfile.TemporaryDirectory() as tmpdir:
		monkeypatch.setattr(appdirs, "user_config_dir", lambda *args: PathPlus(tmpdir))

		example_config = PathPlus(__file__).parent / "example_config"
		tmp_configdir = PathPlus(tmpdir) / "PyCharm2020.2" / "options"
		tmp_configdir.mkdir(parents=True)

		for filename in {"other.xml", "web-browsers.xml"}:
			(tmp_configdir / filename).write_text((example_config / filename).read_text())

		yield tmpdir


def test_get_config_dir(monkeypatch, tmp_pathplus):
	monkeypatch.setattr(appdirs, "user_config_dir", lambda *args: str(tmp_pathplus / "JetBrains"))

	with pytest.raises(FileNotFoundError, match=re_windowspath(f"^{tmp_pathplus / 'JetBrains'}$")):
		get_config_dir()

	(tmp_pathplus / "JetBrains").mkdir()

	with pytest.raises(
			FileNotFoundError,
			match=f"^{re.escape(re_windowspath(str(tmp_pathplus / 'JetBrains' / 'PyCharm[0-9]{4}.[0-9]')))}$",
			):
		get_config_dir()


def test_get_docs_port(mocked_config):
	assert get_docs_port() == 63333


def test_get_docs_port_missing_config(monkeypatch, tmp_pathplus):
	monkeypatch.setattr(appdirs, "user_config_dir", lambda *args: str(tmp_pathplus / "JetBrains"))

	(tmp_pathplus / "JetBrains" / "PyCharm2020.2").mkdir(parents=True)
	options_dir = tmp_pathplus / "JetBrains" / "PyCharm2020.2" / "options"

	with pytest.raises(FileNotFoundError, match=re_windowspath(f"^{options_dir / 'other.xml'}$")):
		get_docs_port()

	options_dir.mkdir()

	with pytest.raises(FileNotFoundError, match=re_windowspath(f"^{options_dir / 'other.xml'}$", )):
		get_docs_port()


def test_open_in_browser_missing_config(monkeypatch, tmp_pathplus):
	monkeypatch.setattr(appdirs, "user_config_dir", lambda *args: str(tmp_pathplus / "JetBrains"))

	(tmp_pathplus / "JetBrains" / "PyCharm2020.2").mkdir(parents=True)
	options_dir = tmp_pathplus / "JetBrains" / "PyCharm2020.2" / "options"

	with pytest.raises(FileNotFoundError, match=re_windowspath(f"^{options_dir / 'web-browsers.xml'}$", )):
		open_in_browser("https://google.com")

	options_dir.mkdir()

	with pytest.raises(FileNotFoundError, match=re_windowspath(f"^{options_dir / 'web-browsers.xml'}$", )):
		open_in_browser("https://google.com")
