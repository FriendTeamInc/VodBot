# Export video data to a specific location

from .stage import StageData

import vodbot.util as util
from vodbot.printer import cprint

import json
from datetime import datetime
from pathlib import Path
from os import listdir as os_listdir, remove as os_remove
from os.path import exists as os_exists, isfile as os_isfile


# Default path
vodbotdir = util.vodbotdir
stagedir = None
tempdir = None


EPOCH = datetime.utcfromtimestamp(0)
def sort_stagedata(stagedata):
	date = datetime.strptime(stagedata.datestring, "%Y/%m/%d")
	return (date - EPOCH).total_seconds()


def load_stage(stage_id):
	jsonread = None
	try:
		with open(str(stagedir / (stage_id+".stage"))) as f:
			jsonread = json.load(f)
	except FileNotFoundError:
		util.exit_prog(46, f'Could not find stage "{stage_id}". (FileNotFound)')
	except KeyError:
		util.exit_prog(46, f'Could not parse stage "{stage_id}" as JSON. Is this file corrupted?')
	
	_title = jsonread['title']
	_desc = jsonread['desc']
	_ss = jsonread['ss']
	_to = jsonread['to']
	_streamers = jsonread['streamers']
	_datestring = jsonread['datestring']
	_filename = jsonread['filename']

	return StageData(_title, _desc, _ss, _to, _streamers, _datestring, _filename)


def run(args):
	conf = util.load_conf(args.conf)
	
	# load stages, but dont slice
	# Handle id/all
	stagedata = None
	stagedatas = None
	if args.id == "all":
		cprint("#dLoading stages...", end=" ")
		# create a list of all the hashes and sort by date streamed, slice chronologically
		stages = [d[:-6] for d in os_listdir(str(stagedir))
			if os_isfile(str(stagedir / d)) and d[-5:] == "stage"]
		stagedatas = [load_stage(stage) for stage in stages]
		stagedatas.sort(key=sort_stagedata)
	else:
		cprint("#dLoading stage...", end=" ")
		# check if stage exists, and prep it for slice
		stagedata = load_stage(args.id)
		cprint(f"About to slice stage {stagedata.hashdigest}.#r")
	
	# export with ffmpeg

	# say "Done!"
