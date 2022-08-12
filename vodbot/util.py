# Module to pull and create different files and directories on the OS

from .printer import cprint
from .config import DEFAULT_CONFIG_SCHEMA

import os
import sys
from marshmallow import ValidationError


def make_dir(directory):
	"""
	Creates the directory structure to house the configuration data and VODs.

	:param directory: A string of where the directory structure should be made.
	"""
	try:
		os.makedirs(str(directory), exist_ok=True)
	except OSError as e:
		exit_prog(code=-3, errmsg=str(e))


def load_conf(filename):
	"""
	Loads the config of VodBot at a specific directory.

	:param filename: File name of the JSON formatted configuration file.
	:returns: Dictionary created from the conf file.
	"""

	conf = None
	try:
		with open(filename) as f:
			conf = DEFAULT_CONFIG_SCHEMA.loads(f.read())
	except FileNotFoundError:
		exit_prog(2, f"Config not found. You can configure VodBot with the init command.")
	except ValidationError as e:
		exit_prog(98, f'Failed to validate config. \n"{e.messages}"')

	return conf


def exit_prog(code=0, errmsg=None):
	"""
	Exits the program with an error code and optional error message.

	:param code: The error code to exit with. Should be unique per exit case.
	:param errmsg: The corresponding error message to print when exiting.
	"""

	print()

	if code != 0:
		msg = f"#r#fR#lERROR! #fY#l({code})#r"
		if errmsg != None:
			msg += " #fR#l" + errmsg + "#r"
		cprint(msg, end=" ")

	cprint("#r#dExiting...#r")
	sys.exit(code)
