# Export video data to a specific location

from .stage import StageData

import vodbot.util as util
from vodbot.printer import cprint

import json
import subprocess
from datetime import datetime
from pathlib import Path
from os import listdir as os_listdir, makedirs as os_mkdir, remove as os_remove
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
	cprint(f"#rSlicing stage `#fM{stagedata.hashdigest}#r` #d({stagedata.ss} - {stagedata.to})#r")

	cmd = [ "ffmpeg", "-ss", stagedata.ss ]

	if stagedata.to != "EOF":
		cmd += ["-to", stagedata.to]

	cmd += [
		"-i", stagedata.filename, "-c", "copy",
		tmpfile, "-y", "-stats", "-loglevel", "warning"
	]

	result = subprocess.run(cmd)

	return result.returncode == 0


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
		os_mkdir(args.path, exist_ok=True)
		args.path = Path(args.path)
		for stage in stagedatas:
			if export_video(args.path, stage) == True:
				# delete stage on success
				os_remove(str(stagedir / f"{stage.hashdigest}.stage"))
			else:
				# have warning message
				cprint(f"#r#fRSkipping stage `{stage.hashdigest}` due to error.#r\n")
	else:
		cprint("#dLoading stage...", end=" ")
		
		# check if stage exists, and prep it for slice
		stagedata = load_stage(args.id)
		
		# Export with ffmpeg
		os_mkdir(args.path, exist_ok=True)
		args.path = Path(args.path)
		if export_video(args.path, stagedata) == True:
			# delete stage on success
			os_remove(str(stagedir / f"{stagedata.hashdigest}.stage"))
		else:
			# have warning message
			cprint(f"#r#fRSkipping stage `{stagedata.hashdigest}` due to error.")

	# say "Done!"
	cprint("#fG#lDone!#r")