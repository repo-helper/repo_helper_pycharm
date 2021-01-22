#!/usr/bin/env python3
#
#  iml_manager.py
"""
Class to update PyCharm's ``*.iml`` configuration files.
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
import posixpath

# 3rd party
import click
import lxml  # type: ignore
import lxml.etree  # type: ignore
from consolekit.utils import coloured_diff
from domdf_python_tools.paths import PathPlus, unwanted_dirs
from domdf_python_tools.stringlist import StringList
from domdf_python_tools.typing import PathLike
from lxml import objectify
from repo_helper.core import RepoHelper

__all__ = ["ImlManager"]


class ImlManager:
	"""
	Class to update PyCharm's ``*.iml`` configuration files.

	:param repo_dir:
	"""

	excluded_dirs = {
			*unwanted_dirs,
			"build",
			"dist",
			"conda",
			}

	def __init__(self, repo_dir: PathLike):
		self.rh = RepoHelper(repo_dir)

		if not (self.rh.target_repo / ".idea").is_dir():  # pragma: no cover
			raise FileNotFoundError("'.idea' directory not found. Perhaps this isn't a PyCharm project?")

		try:
			self.module_file: PathPlus = next((self.rh.target_repo / ".idea").glob("*.iml"))
		except StopIteration:
			raise FileNotFoundError("No '.idea/*.iml' file found. Perhaps this isn't a PyCharm project?")

		module_config = objectify.parse(str(self.module_file))
		self.root = module_config.getroot()

		self.excluded_dirs = set(self.excluded_dirs)
		self.excluded_dirs.add(posixpath.join(self.rh.templates.globals["docs_dir"], "build"))

	def run(self, show_diff: bool = False) -> int:
		"""

		:param show_diff: Whether to show a diff if changes are made.
		"""

		self.update_excludes()
		self.update_runner()
		self.remove_docstring_format()
		return self.write_out(show_diff)

	def write_out(self, show_diff: bool = False) -> int:
		"""

		:param show_diff: Whether to show a diff if changes are made.
		"""

		modified_xml = StringList(['<?xml version="1.0" encoding="UTF-8"?>'])
		modified_xml.append(lxml.etree.tostring(self.root, pretty_print=True).decode("UTF-8"))
		modified_xml.blankline(ensure_single=True)

		current_content = self.module_file.read_lines()

		changed = current_content != list(modified_xml)

		if not changed:
			return 0

		if show_diff:
			click.echo(
					coloured_diff(
							current_content,
							list(modified_xml),
							self.module_file.name,
							self.module_file.name,
							"(original)",
							"(updated)",
							lineterm='',
							)
					)

		self.module_file.write_lines(modified_xml)

		return 1

	def update_excludes(self) -> None:
		"""
		Update the list of directories which should be excluded from indexing.
		"""

		file_module_dir = "file://$MODULE_DIR$/"

		for component in self.root.findall("component"):
			if component.attrib["name"] != "NewModuleRootManager":
				continue

			# TODO: handle component not existing

			for exclude_node in component.content.findall("excludeFolder"):
				self.excluded_dirs.add(
						exclude_node.attrib.get(
								"url",
								f"{file_module_dir}.mypy_cache",
								).split(file_module_dir)[-1],
						)
				component.content.remove(exclude_node)

			# print(excluded_dirs)

			for directory in sorted(self.excluded_dirs):
				node = lxml.objectify.StringElement()
				node.tag = "excludeFolder"
				node.attrib["url"] = file_module_dir + directory
				component.content.append(node)

		return

	def update_runner(self) -> None:
		"""
		Set the project's test runner to pytest.
		"""

		for component in self.root.findall("component"):
			if component.attrib["name"] != "TestRunnerService":
				continue

			for option in component.findall("option"):
				if option.attrib["name"] == "PROJECT_TEST_RUNNER":
					option.attrib["value"] = "pytest"

		return

	def remove_docstring_format(self) -> None:
		"""
		Remove any existing option for "PyDocumentationSettings", to revert to the default of reStructuredText.
		"""

		for component in self.root.findall("component"):
			if component.attrib["name"] == "PyDocumentationSettings":
				self.root.remove(component)
				return

		return
