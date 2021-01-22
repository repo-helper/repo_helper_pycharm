#!/usr/bin/env python3
#
#  __init__.py
"""
repo_helper extension to manage PyCharm's configuration.
"""
#
#  Copyright © 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#  OR OTHER DEALINGS IN THE SOFTWARE.
#

# stdlib
from functools import partial, reduce

# 3rd party
import click
from consolekit import CONTEXT_SETTINGS
from repo_helper.cli import cli_group

__author__: str = "Dominic Davis-Foster"
__copyright__: str = "2020 Dominic Davis-Foster"
__license__: str = "MIT License"
__version__: str = "0.2.1"
__email__: str = "dominic@davis-foster.co.uk"

__all__ = ["configure", "pycharm", "schema", "docs"]


@cli_group()
def pycharm() -> None:
	"""
	Manage PyCharm config.
	"""


pycharm_command = partial(pycharm.command, context_settings=CONTEXT_SETTINGS)


@pycharm_command()
def schema() -> None:
	"""
	Register the schema mapping for 'repo_helper.yml' with PyCharm.
	"""

	# 3rd party
	from consolekit.utils import abort
	from domdf_python_tools.paths import PathPlus

	# this package
	from repo_helper_pycharm.register_schema import register_schema

	try:
		register_schema(PathPlus.cwd())
	except FileNotFoundError as e:
		raise abort(str(e))


@click.option("--diff", is_flag=True, default=False, help="Show a diff if changes are made.")
@pycharm_command()
def configure(diff: bool = False) -> None:
	"""
	Set the basic configuration for PyCharm.
	"""

	# stdlib
	import sys

	# 3rd party
	from consolekit.utils import abort
	from domdf_python_tools.paths import PathPlus

	# this package
	from repo_helper_pycharm.iml_manager import ImlManager

	try:
		iml_manager = ImlManager(PathPlus.cwd())
	except FileNotFoundError as e:
		raise abort(str(e))

	sys.exit(iml_manager.run(diff))


@pycharm_command()
def docs() -> None:
	"""
	Open the documentation using PyCharm's built-in web server.
	"""

	# stdlib
	import operator

	# 3rd party
	from apeye import URL
	from consolekit.utils import abort
	from domdf_python_tools.paths import PathPlus
	from repo_helper.core import RepoHelper

	# this package
	from repo_helper_pycharm.docs import get_docs_port, open_in_browser

	rh = RepoHelper(PathPlus.cwd())

	if not rh.templates.globals["enable_docs"]:
		raise abort("The current project has no documentation!")
	else:
		url = reduce(
				operator.truediv,
				[
						URL(f"http://localhost:{get_docs_port()}"),
						rh.target_repo.name,
						rh.templates.globals["docs_dir"],
						"build",
						"html",
						]
				)

		open_in_browser(url)
