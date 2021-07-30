# Export video data to a specific location

from .stage import StageData

import vodbot.util as util
from vodbot.printer import cprint

import json
import subprocess
from datetime import datetime
from pathlib import Path
from os import listdir as os_listdir, mkdir as os_mkdir
from os.path import isfile as os_isfile


# Default path
vodbotdir = util.vodbotdir
stagedir = None


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


def export_video(pathout: Path, stagedata: StageData):
	tmpfile = str(pathout / f"{stagedata.title}.mp4")
	print(f"Slicing stage `{stagedata.hashdigest}` video ({stagedata.ss} - {stagedata.to})")
	cmd = [
		"ffmpeg", "-ss", stagedata.ss,
	]
	if stagedata.to != "EOF":
		cmd += ["-to", stagedata.to]
	cmd += [
		"-i", stagedata.filename,
		"-c", "copy",
		tmpfile, "-y", "-stats",
		"-loglevel", "warning"
	]
	result = subprocess.run(cmd)


def run(args):
	global stagedir

	conf = util.load_conf(args.config)
	stagedir = Path(conf["stage_dir"])
	
	# load stages, but dont slice
	# Handle id/all
	if args.id == "all":
		cprint("#dLoading and slicing stages...#r")

		# create a list of all the hashes and sort by date streamed, slice chronologically
		stages = [d[:-6] for d in os_listdir(str(stagedir))
			if os_isfile(str(stagedir / d)) and d[-5:] == "stage"]
		stagedatas = [load_stage(stage) for stage in stages]
		stagedatas.sort(key=sort_stagedata)

		# Export with ffmpeg
		os_mkdir(args.path)
		args.path = Path(args.path)
		for stage in stagedatas:
			cprint(f"\rAbout to slice stage {stage.hashdigest}.#r")
			export_video(args.path, stage)
	else:
		cprint("#dLoading stage...", end=" ")
		
		# check if stage exists, and prep it for slice
		stagedata = load_stage(args.id)
		cprint(f"About to slice stage {stagedata.hashdigest}.#r")
		
		# Export with ffmpeg
		args.path = Path(args.path)
		export_video(args.path, stagedata)

	# say "Done!"
	cprint("#fG#lDone!#r")
