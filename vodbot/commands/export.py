# Export video data to a specific location

from .stage import StageData

import vodbot.util as util
from vodbot.printer import cprint

import json
import subprocess
from datetime import datetime
from pathlib import Path
from os import listdir as os_listdir, remove as os_remove
from os.path import isfile as os_isfile


# Default path
vodbotdir = util.vodbotdir
stagedir = None


EPOCH = datetime.utcfromtimestamp(0)
def sort_stagedata(stagedata):
	date = datetime.strptime(stagedata.datestring, "%Y/%m/%d")
	return (date - EPOCH).total_seconds()


def export_video(pathout: Path, stagedata: StageData):
	tmpfile = str(pathout / f"{stagedata.title}.mp4")
	cprint(f"#rSlicing stage `#fM{stagedata.id}#r` #d({stagedata.ss} - {stagedata.to})#r")

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
		stagedatas = StageData.load_all_stages(stagedir)
		stagedatas.sort(key=sort_stagedata)
		print(stagedatas)

		# Export with ffmpeg
		util.make_dir(args.path)
		args.path = Path(args.path)
		for stage in stagedatas:
			if export_video(args.path, stage) == True:
				# delete stage on success
				os_remove(str(stagedir / f"{stage.id}.stage"))
			else:
				# have warning message
				cprint(f"#r#fRSkipping stage `{stage.id}` due to error.#r\n")
	else:
		cprint("#dLoading stage...", end=" ")
		
		# check if stage exists, and prep it for slice
		stagedata = StageData.load_from_id(stagedir, args.id)
		
		# Export with ffmpeg
		util.make_dir(args.path)
		args.path = Path(args.path)
		if export_video(args.path, stagedata) == True:
			# delete stage on success
			os_remove(str(stagedir / f"{stagedata.id}.stage"))
		else:
			# have warning message
			cprint(f"#r#fRSkipping stage `{stagedata.id}` due to error.")

	# say "Done!"
	cprint("#fG#lDone!#r")
