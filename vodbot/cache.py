# Module for the cache dataclass
# dedicated type for easier processing of info

from vodbot.util import exit_prog
from .config import Config

import json
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from pathlib import Path
from typing import Dict, List
from os import listdir as os_listdir
from os.path import isfile as os_isfile, exists as os_exists

# channels property maps a login name to a channel object
# vods property maps a VOD ID to its local meta filename
# clips property maps a Clip ID to its local meta filename
# slugs property maps a Clip slug to its local meta filename


@dataclass_json
@dataclass
class _CacheChannel:
	vods: Dict[str, str]
	clips: Dict[str, str]
	slugs: Dict[str, str]

@dataclass_json
@dataclass
class Cache:
	channels: Dict[str, _CacheChannel] = field(default_factory={})


_cached_cache = None
def load_cache(conf: Config, update_cache: bool = False) -> Cache:
	"""
	Loads a cache JSON file, containing ID's for Users, VODs, and Clips.
	"""
	global _cached_cache

	cachepath = conf.directories.temp / "cache.json"

	if _cached_cache is None or update_cache:
		# check if cache exists
		if not update_cache and os_exists(cachepath) and os_isfile(cachepath):
			with open(cachepath) as f:
				_cached_cache = Cache.loads(f.read())
		elif update_cache:
			_cached_cache = _refresh_cache()
			save_cache(conf, _cached_cache)
		else:
			# manually create cache
			_cached_cache = Cache.from_dict({})
			save_cache(conf, _cached_cache)
	
	return _cached_cache


def _refresh_cache(conf: Config):
	# here we manually refresh the cache by examining all the important stuff.

	newchannels = {}

	for channel in conf.channels:
		login = channel.username

		voddir = conf.directories.vods / login
		vods = { d.split("_")[1][:-5]: d
			for d in os_listdir(voddir)
				if os_isfile(voddir / d) and d.endswith(".meta")
		}

		clipdir = conf.directories.clips / login
		clips = { d.split("_")[1][:-5]: d
			for d in os_listdir(clipdir)
				if os_isfile(clipdir / d) and d.endswith(".meta")
		}

		slugs = {}
		for id, filename in clips.items():
			clipinfo = None
			try:
				with open(clipdir / filename, "r") as f:
					clipinfo = json.load(f)
			except FileNotFoundError:
				exit_prog(2, f"Clip `{id}` not found. Did you move it?")
			except json.JSONDecodeError as e:
				exit_prog(97, f'Failed to parse clip `{id}` metadata. "{e}"')

			slug = clipinfo.get("slug")
			if slug is None:
				# warn: could not get slug for clip
				continue

			slugs[slug] = filename
		
		newchannel = _CacheChannel.from_dict({"vods": vods, "clips": clips, "slugs": slugs})
		newchannels[login] = newchannel
	
	return Cache.from_dict(newchannels)


def save_cache(conf: Config, cache: Cache) -> None:
	"""
	Saves a cache JSON file to the temp directory
	"""
	global _cached_cache

	_cached_cache = cache

	with open(conf.directories.temp / "cache.json") as f:
		f.write(cache.to_json())
