# 3rd party
import pytest
from domdf_python_tools.paths import PathPlus

pytest_plugins = ("coincidence", "repo_helper.testing", "consolekit.testing")


@pytest.fixture()
def tmp_project(tmp_pathplus: PathPlus, example_config):
	(tmp_pathplus / "repo_helper.yml").write_clean(example_config)


@pytest.fixture(scope="session")
def no_idea():
	return "'.idea' directory not found. Perhaps this isn't a PyCharm project?"
