# 3rd party
import pytest

pytest_plugins = ("coincidence", "repo_helper.testing")


@pytest.fixture()
def tmp_project(tmp_pathplus, example_config):
	(tmp_pathplus / "repo_helper.yml").write_clean(example_config)


@pytest.fixture(scope="session")
def no_idea():
	return "'.idea' directory not found. Perhaps this isn't a PyCharm project?"
