# stdlib
from typing import Union

# 3rd party
import pytest
from coincidence.regressions import AdvancedFileRegressionFixture
from consolekit.testing import CliRunner, Result
from domdf_python_tools.paths import PathPlus, in_directory
from domdf_python_tools.stringlist import StringList

# this package
from repo_helper_pycharm import configure
from repo_helper_pycharm.iml_manager import ImlManager

iml_contents = """\
<?xml version="1.0" encoding="UTF-8"?>
<module type="PYTHON_MODULE" version="4">
  <component name="NewModuleRootManager">
    <content url="file://$MODULE_DIR$">
      <excludeFolder url="file://$MODULE_DIR$/venv" />
    </content>
    <orderEntry type="inheritedJdk" />
    <orderEntry type="sourceFolder" forTests="false" />
  </component>
  <component name="PackageRequirementsSettings">
    <option name="requirementsPath" value="" />
  </component>
  <component name="PyDocumentationSettings">
    <option name="format" value="PLAIN" />
    <option name="myDocStringFormat" value="Plain" />
  </component>
  <component name="TestRunnerService">
    <option name="PROJECT_TEST_RUNNER" value="nose" />
  </component>
</module>
"""


class BaseTest:

	def check_output(
			self,
			tmp_pathplus: PathPlus,
			advanced_file_regression: AdvancedFileRegressionFixture,
			stdout: Union[str, StringList],
			) -> None:

		stdout = StringList(stdout)
		stdout.blankline(ensure_single=True)

		advanced_file_regression.check(stdout, extension=".patch")
		advanced_file_regression.check_file(tmp_pathplus / ".idea" / "repo_helper_demo.iml", extension=".xml")

	@staticmethod
	def make_fake_iml(tmp_pathplus: PathPlus) -> None:
		(tmp_pathplus / ".idea").maybe_make()
		(tmp_pathplus / ".idea" / "repo_helper_demo.iml").write_clean(iml_contents)


# TODO: check when file exists


class TestCommand(BaseTest):

	@pytest.mark.usefixtures("tmp_project")
	def test_iml_manager_not_project(self, no_idea: str, tmp_pathplus: PathPlus) -> None:

		with in_directory(tmp_pathplus):
			runner = CliRunner(mix_stderr=False)
			result: Result = runner.invoke(configure, catch_exceptions=False)
			assert result.exit_code == 1
			assert result.stderr == f"{no_idea}\nAborted!\n"
			assert not result.stdout

	@pytest.mark.parametrize("diff", [True, False])
	@pytest.mark.usefixtures("tmp_project")
	def test_iml_manager(
			self,
			tmp_pathplus: PathPlus,
			advanced_file_regression: AdvancedFileRegressionFixture,
			diff: bool,
			cli_runner: CliRunner
			) -> None:

		self.make_fake_iml(tmp_pathplus)

		with in_directory(tmp_pathplus):
			result: Result = cli_runner.invoke(
					configure,
					catch_exceptions=False,
					args=["--diff"] if diff else [],
					)
			assert result.exit_code == 1

		self.check_output(tmp_pathplus, advanced_file_regression, result.stdout)


class TestClass(BaseTest):

	@pytest.mark.usefixtures("tmp_project")
	def test_iml_manager_not_project(self, tmp_pathplus: PathPlus, no_idea: str) -> None:

		with pytest.raises(FileNotFoundError, match=no_idea):
			ImlManager(tmp_pathplus)

	@pytest.mark.parametrize("diff", [True, False])
	@pytest.mark.usefixtures("tmp_project")
	def test_iml_manager(
			self,
			tmp_pathplus: PathPlus,
			advanced_file_regression: AdvancedFileRegressionFixture,
			capsys,
			diff: bool,
			) -> None:
		self.make_fake_iml(tmp_pathplus)

		assert ImlManager(tmp_pathplus).run(diff) == 1

		self.check_output(tmp_pathplus, advanced_file_regression, capsys.readouterr().out)
