#!/usr/bin/env python3
#
#  iml_manager.py
"""
Register the schema mapping for ``repo_helper.yml`` with PyCharm.
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
from textwrap import dedent, indent

# 3rd party
import repo_helper
from domdf_python_tools.compat import importlib_resources
from domdf_python_tools.typing import PathLike
from domdf_python_tools.words import TAB
from lxml import etree, objectify  # type: ignore
from repo_helper.configuration import dump_schema
from repo_helper.core import RepoHelper

__all__ = ["register_schema"]


def register_schema(repo_dir: PathLike) -> None:
	"""
	Register the schema mapping for ``repo_helper.yml`` with PyCharm.

	:param repo_dir:
	"""

	rh = RepoHelper(repo_dir)

	schema_mapping_file = rh.target_repo / ".idea/jsonSchemas.xml"

	if not schema_mapping_file.parent.is_dir():  # pragma: no cover
		raise FileNotFoundError("'.idea' directory not found. Perhaps this isn't a PyCharm project?")

	dump_schema()

	with importlib_resources.path(repo_helper, "repo_helper_schema.json") as schema_file:

		entry_xml = f"""\
		<entry key="repo_helper_schema">
			<value>
				<SchemaInfo>
					<option name="name" value="repo_helper_schema" />
					<option name="relativePathToSchema" value="{str(schema_file)}" />
					<option name="patterns">
						<list>
							<Item>
								<option name="path" value="repo_helper.yml" />
							</Item>
						</list>
					</option>
				</SchemaInfo>
			</value>
		</entry>
		"""

		entry_xml = indent(dedent(entry_xml), '\t').expandtabs(4)

	if not schema_mapping_file.is_file():
		mapping_xml = f"""\
	<?xml version="1.0" encoding="UTF-8"?>
	<project version="4">
		<component name="JsonSchemaMappingsProjectConfiguration">
			<state>
				<map>
	{indent(entry_xml, TAB*4)[1:-1]}
				</map>
			</state>
		</component>
	</project>
	"""

		schema_mapping_file.write_clean(dedent(mapping_xml).expandtabs(4))

	else:
		schema = objectify.parse(str(schema_mapping_file))
		root = schema.getroot()
		# printr(root)

		for entry in root.component.state.map.findall("entry"):
			# printr(entry)
			if entry.attrib["key"] == "repo_helper_schema":
				break
		else:
			root.component.state.map.append(objectify.fromstring(entry_xml))
			schema_mapping_file.write_clean(etree.tostring(root, pretty_print=True).decode("UTF-8"))
