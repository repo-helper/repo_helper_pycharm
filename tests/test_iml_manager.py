# stdlib
from typing import Union

# 3rd party
import pytest
from click.testing import CliRunner, Result
from coincidence import check_file_output, check_file_regression
from domdf_python_tools.paths import PathPlus, in_directory
from domdf_python_tools.stringlist import StringList
from pytest_regressions.file_regression import FileRegressionFixture

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
			file_regression: FileRegressionFixture,
			stdout: Union[str, StringList],
			):

		stdout = StringList(stdout)
		stdout.blankline(ensure_single=True)

		check_file_regression(stdout, file_regression, extension=".patch")
		check_file_output(tmp_pathplus / ".idea" / "repo_helper_demo.iml", file_regression, extension=".xml")

	def make_fake_iml(self, tmp_pathplus: PathPlus):
		(tmp_pathplus / ".idea").maybe_make()
		(tmp_pathplus / ".idea" / "repo_helper_demo.iml").write_clean(iml_contents)


# TODO: check when file exists


class TestCommand(BaseTest):

	@pytest.mark.usefixtures("tmp_project")
	def test_iml_manager_not_project(
			self,
			no_idea,
			tmp_pathplus: PathPlus,
			file_regression: FileRegressionFixture,
			tmp_project,
			):

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
			file_regression: FileRegressionFixture,
			diff: bool,
			):

		self.make_fake_iml(tmp_pathplus)

		with in_directory(tmp_pathplus):
			runner = CliRunner()
			result: Result = runner.invoke(
					configure,
					catch_exceptions=False,
					args=["--diff"] if diff else [],
					)
			assert result.exit_code == 1

		self.check_output(tmp_pathplus, file_regression, result.stdout)


class TestClass(BaseTest):

	@pytest.mark.usefixtures("tmp_project")
	def test_iml_manager_not_project(self, tmp_pathplus: PathPlus, no_idea):

		with pytest.raises(FileNotFoundError, match=no_idea):
			ImlManager(tmp_pathplus)

	@pytest.mark.parametrize("diff", [True, False])
	@pytest.mark.usefixtures("tmp_project")
	def test_iml_manager(
			self,
			tmp_pathplus: PathPlus,
			file_regression: FileRegressionFixture,
			capsys,
			diff,
			):
		self.make_fake_iml(tmp_pathplus)

		assert ImlManager(tmp_pathplus).run(diff) == 1

		self.check_output(tmp_pathplus, file_regression, capsys.readouterr().out)
