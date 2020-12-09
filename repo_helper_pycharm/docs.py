#!/usr/bin/env python3
#
#  docs.py
"""
Parse PyCharm configuration and open a project's documentation in the default web browser.

.. versionadded:: 0.2.0
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
import os
import webbrowser
from typing import Optional

# 3rd party
import appdirs  # type: ignore
from domdf_python_tools.iterative import natmax
from domdf_python_tools.paths import PathPlus
from lxml import objectify  # type: ignore

__all__ = [
		"get_config_dir",
		"open_in_browser",
		"get_docs_port",
		]


def get_config_dir() -> PathPlus:
	"""
	Returns the path to the PyCharm configuration directory.

	:raises: :exc:`FileNotFoundError` if the directory can't be found.

	.. versionadded:: 0.2.0
	"""

	config_dir = PathPlus(appdirs.user_config_dir("JetBrains"))

	if not config_dir.is_dir():
		raise FileNotFoundError(config_dir)

	try:
		return config_dir / natmax([p.name for p in config_dir.glob("PyCharm*")])
	except (ValueError, IndexError):
		raise FileNotFoundError(config_dir / "PyCharm[0-9]{4}.[0-9]") from None


def open_in_browser(url: str) -> None:
	"""
	Opens the URL in the browser configured in the PyCharm settings.

	:param url:

	.. versionadded:: 0.2.0
	"""

	config_dir = get_config_dir()
	browser_config_file = config_dir / "options" / "web-browsers.xml"

	if not browser_config_file.is_file():
		raise FileNotFoundError(browser_config_file)

	browser_config = objectify.parse(str(browser_config_file))
	root = browser_config.getroot()

	assert root.component.attrib["name"] == "WebBrowsersConfiguration"
	default = root.component.attrib["default"]

	browsers = [browser for browser in root.component.findall("browser")]

	if default == "first":
		browser_name = browsers[0].attrib["name"].lower()
		if browser_name == "firefox":
			try:
				profile: Optional[str] = str(browsers[0].settings.profile)
			except AttributeError:
				profile = None

			if profile is not None:
				os.system(f"firefox -P {profile} {url}")
			else:
				os.system(f"firefox {url}")

		else:
			webbrowser.get(browsers[0].attrib["name"].lower())

	else:
		raise NotImplementedError(default)


def get_docs_port() -> int:
	"""
	Returns the number of the port used by the PyCharm web server.

	.. versionadded:: 0.2.0
	"""

	config_dir = get_config_dir()
	other_config_file = config_dir / "options" / "other.xml"

	if not other_config_file.is_file():
		raise FileNotFoundError(other_config_file)

	other_config = objectify.parse(str(other_config_file))

	root = other_config.getroot()

	for tag in root.getchildren():
		if tag.tag == "component" and tag.attrib["name"] == "BuiltInServerOptions":
			return int(tag.attrib["builtInServerPort"])

	raise ValueError
