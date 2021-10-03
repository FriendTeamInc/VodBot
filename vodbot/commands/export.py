# Export video data to a specific location

from .stage import StageData

import vodbot.util as util
import vodbot.video as vbvid
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
			tmpfile = None
			try:
				tmpfile = vbvid.process_stage(conf, stage)
				os_remove(str(stagedir / f"{stage.id}.stage"))
			except vbvid.FailedToSlice as e:
				cprint(f"#r#fRSkipping stage `{stage.id}`, failed to slice video with ID of `{e.vid}`.#r\n")
			except vbvid.FailedToConcat:
				cprint(f"#r#fRSkipping stage `{stage.id}`, failed to concatenate videos.#r\n")
			except vbvid.FailedToCleanUp as e:
				cprint(f"#r#fRSkipping stage `{stage.id}`, failed to clean up temp files.#r\n\n{e.vid}")
	else:
		cprint("#dLoading stage...", end=" ")
		
		# check if stage exists, and prep it for slice
		stagedata = StageData.load_from_id(stagedir, args.id)
		
		# Export with ffmpeg
		util.make_dir(args.path)
		args.path = Path(args.path)
		
		tmpfile = None
		try:
			tmpfile = vbvid.process_stage(conf, stagedata)
			if conf["stage_export_delete"]:
				os_remove(str(stagedir / f"{stagedata.id}.stage"))
				
		except vbvid.FailedToSlice as e:
			cprint(f"#r#fRSkipping stage `{stagedata.id}`, failed to slice video with ID of `{e.vid}`.#r\n")
		except vbvid.FailedToConcat:
			cprint(f"#r#fRSkipping stage `{stagedata.id}`, failed to concatenate videos.#r\n")
		except vbvid.FailedToCleanUp as e:
			cprint(f"#r#fRSkipping stage `{stagedata.id}`, failed to clean up temp files.#r\n\n{e.vid}")

	# say "Done!"
	cprint("#fG#lDone!#r")
