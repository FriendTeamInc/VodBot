# Module to pull and create different files and directories on the OS

from .printer import cprint
from .config import Config, DEFAULT_CONFIG_SCHEMA

import os
import sys
from json.decoder import JSONDecodeError
from marshmallow import ValidationError
from typing import Tuple
from shutil import which


# time in seconds to a timestamp string
def int_to_timestamp(i:int) -> str:
	if i >= 3600: # hours position
		return f"{int(i // 3600)}:{int((i // 60) % 60)}:{int(i % 60)}"
	elif i >= 60: # minutes position
		return f"0:{int(i // 60)}:{int(i % 60)}"
	else:
		return f"0:0:{int(i)}"


# position and duration to a proper timestamp string
def posdur_to_timestamp(pos:int, dur:int) -> Tuple[str, str]:
	return (int_to_timestamp(pos), int_to_timestamp(pos + dur))


# number of seconds to a duration string
def format_duration(total_seconds:int):
	total_seconds = int(total_seconds)
	hours = total_seconds // 3600
	remainder = total_seconds % 3600
	minutes = remainder // 60
	seconds = total_seconds % 60

	if hours:
		return f"{hours}h{minutes}m{seconds}s"
	elif minutes:
		return f"{minutes}m{seconds}s"
	else:
		return f"{seconds}s"


def timestring_as_seconds(time:str, default:int=0):
	if time == "EOF":
		return default
	
	s = time.split(":")
	
	seconds = int(s[-1]) if len(s) >= 1 else 0
	minutes = int(s[-2]) if len(s) >= 2 else 0
	hours = int(s[-3]) if len(s) >= 3 else 0

	# Hours, minutes, seconds
	return hours * 60 * 60 + minutes * 60 + seconds


def format_size(bytes_:int, digits:int=1, include_units:bool=True) -> str:
	units = ["B", "KB", "MB", "GB", "PB", "EB"]
	for u in units:
		if bytes_ < 1000:
			t = ""
			if digits > 0:
				t = f"{bytes_:.{digits}f}"
			else:
				t = f"{bytes_:d}"
			return f"{t} {u}" if include_units else t
		bytes_ /= 1000

	t = ""
	if digits > 0:
		t = f"{bytes_:.{digits}f}"
	else:
		t = f"{bytes_:d}"
	
	return f"{t} ZB" if include_units else t


_has_ffmpeg = which("ffmpeg") is not None
def has_ffmpeg() -> bool:
	return _has_ffmpeg


def make_dir(directory):
	"""
	Creates the directory structure to house the configuration data and VODs.

	:param directory: A string of where the directory structure should be made.
	"""
	try:
		os.makedirs(str(directory), exist_ok=True)
	except OSError as e:
		exit_prog(code=-3, errmsg=str(e))


# only one config per running instance.
_cached_config = None
def load_conf_wrapper(filename) -> Config:
	global _cached_config
	
	if _cached_config is None:
		with open(filename) as f:
			_cached_config = DEFAULT_CONFIG_SCHEMA.loads(f.read())
	
	return _cached_config


def load_conf(filename) -> Config:
	"""
	Loads a VodBot JSON configuration file.

	:param filename: File name of the JSON formatted configuration file.
	:returns: Config class with all members configured by the input file.
	"""

	conf = None
	try:
		conf = load_conf_wrapper(filename)
	except FileNotFoundError:
		exit_prog(2, f"Config not found. You can configure VodBot with the init command.")
	except JSONDecodeError as e:
		exit_prog(97, f'Failed to parse config. "{e}"')
	except ValidationError as e:
		exit_prog(98, f'Failed to validate config. "{e.messages}"')
	except TypeError as e:
		exit_prog(96, f'Failed to validate config. "{e}"')
	except KeyError as e:
		exit_prog(95, f'Failed to find required key in config. "{e}"')

	return conf


def exit_prog(code=0, errmsg=None):
	"""
	Exits the program with an error code and optional error message.

	:param code: The error code to exit with. Should be unique per exit case.
	:param errmsg: The corresponding error message to print when exiting.
	"""
	
	from .webhook import send_error

	# exit
	print()
	if code != 0:
		msg = f"#r#fR#lERROR! #fY#l({code})#r"
		if errmsg != None:
			msg += " #fR#l" + errmsg + "#r"
		cprint(msg, end=" ")
		send_error(msg)

	cprint("#r#dExiting...#r")
	sys.exit(code)
