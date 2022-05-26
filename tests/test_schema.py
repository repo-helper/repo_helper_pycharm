# stdlib
import os
import re
from abc import abstractmethod

# 3rd party
import pytest
from coincidence.regressions import AdvancedFileRegressionFixture
from consolekit.testing import CliRunner, Result
from domdf_python_tools.paths import PathPlus, in_directory

# this package
from repo_helper_pycharm import schema
from repo_helper_pycharm.register_schema import register_schema


class BaseTest:

	# TODO: check when file exists

	if os.sep == '/':

		def check_output(
				self,
				tmp_pathplus: PathPlus,
				advanced_file_regression: AdvancedFileRegressionFixture,
				stdout: str,
				) -> None:
			assert re.match(
					r"Wrote schema to .*/repo_helper/repo_helper_schema\.json",
					stdout.splitlines()[0],
					)

			file_content = re.sub(
					'value=".*/repo_helper/repo_helper_schema.json"',
					'value="repo_helper/repo_helper_schema.json"',
					(tmp_pathplus / ".idea/jsonSchemas.xml").read_text(),
					)
			advanced_file_regression.check(file_content, extension=".xml")
	else:

		def check_output(
				self,
				tmp_pathplus: PathPlus,
				advanced_file_regression: AdvancedFileRegressionFixture,
				stdout: str,
				) -> None:
			assert re.match(
					r"Wrote schema to .*\\repo_helper\\repo_helper_schema\.json",
					stdout.splitlines()[0],
					)

			file_content = re.sub(
					r'value=".*\\repo_helper\\repo_helper_schema.json"',
					r'value="repo_helper\\repo_helper_schema.json"',
					(tmp_pathplus / ".idea/jsonSchemas.xml").read_text(),
					)
			advanced_file_regression.check(file_content, extension=".xml")

	@pytest.mark.usefixtures("tmp_project")
	@pytest.mark.skipif(condition=os.sep == '\\', reason="Different test for platforms where os.sep == \\")
	def test_pycharm_schema_forward(
			self,
			tmp_pathplus: PathPlus,
			advanced_file_regression: AdvancedFileRegressionFixture,
			capsys,
			) -> None:
		self.run_test(tmp_pathplus, advanced_file_regression, capsys)

	@pytest.mark.skipif(condition=os.sep == '/', reason="Different test for platforms where os.sep == /")
	@pytest.mark.usefixtures("tmp_project")
	def test_pycharm_schema_back(
			self,
			tmp_pathplus: PathPlus,
			advanced_file_regression: AdvancedFileRegressionFixture,
			capsys,
			) -> None:
		self.run_test(tmp_pathplus, advanced_file_regression, capsys)

	@abstractmethod
	def run_test(
			self,
			tmp_pathplus: PathPlus,
			advanced_file_regression: AdvancedFileRegressionFixture,
			capsys,
			) -> None:
		raise NotImplementedError


class TestCommand(BaseTest):

	@pytest.mark.usefixtures("tmp_project")
	def test_pycharm_schema_not_project(self, no_idea: str, tmp_pathplus) -> None:
		with in_directory(tmp_pathplus):
			runner = CliRunner(mix_stderr=False)
			result: Result = runner.invoke(schema, catch_exceptions=False)
			assert result.exit_code == 1
			assert result.stderr == f"{no_idea}\nAborted!\n"
			assert not result.stdout

	def run_test(
			self,
			tmp_pathplus: PathPlus,
			advanced_file_regression: AdvancedFileRegressionFixture,
			capsys,
			) -> None:
		(tmp_pathplus / ".idea").maybe_make()

		with in_directory(tmp_pathplus):
			runner = CliRunner()
			result: Result = runner.invoke(schema, catch_exceptions=False)
			assert result.exit_code == 0

		self.check_output(tmp_pathplus, advanced_file_regression, result.stdout)


class TestFunction(BaseTest):

	@pytest.mark.usefixtures("tmp_project")
	def test_pycharm_schema_not_project(self, tmp_pathplus, no_idea):
		with pytest.raises(FileNotFoundError, match=no_idea):
			register_schema(tmp_pathplus)

	def run_test(
			self,
			tmp_pathplus: PathPlus,
			advanced_file_regression: AdvancedFileRegressionFixture,
			capsys,
			) -> None:
		(tmp_pathplus / ".idea").maybe_make()
		register_schema(tmp_pathplus)
		self.check_output(tmp_pathplus, advanced_file_regression, capsys.readouterr().out)
