# Export video data to a specific location

from .stage import StageData

import vodbot.util as util
import vodbot.video as vbvid
import vodbot.chatlog as vbchat
from vodbot.printer import cprint

from datetime import datetime
from pathlib import Path
from os import remove as os_remove, replace as os_replace


# Default path
vodbotdir = util.vodbotdir
stagedir = None


EPOCH = datetime.utcfromtimestamp(0)
def sort_stagedata(stagedata):
	date = datetime.strptime(stagedata.datestring, "%Y/%m/%d")
	return (date - EPOCH).total_seconds()


def handle_stage(conf: dict, stagedir: Path, stage: StageData) -> Path:
	tmpfile = None
	try:
		tmpfile = vbvid.process_stage(conf, stage)
	except vbvid.FailedToSlice as e:
		cprint(f"#r#fRSkipping stage `{stage.id}`, failed to slice video with ID of `{e.vid}`.#r\n")
		return None
	except vbvid.FailedToConcat:
		cprint(f"#r#fRSkipping stage `{stage.id}`, failed to concatenate videos.#r\n")
		return None
	except vbvid.FailedToCleanUp as e:
		cprint(f"#r#fRSkipping stage `{stage.id}`, failed to clean up temp files.#r\n\n{e.vid}")
		return None
	
	return tmpfile


def run(args):
	global stagedir

	conf = util.load_conf(args.config)
	stagedir = Path(conf["stage_dir"])

	util.make_dir(args.path)
	args.path = Path(args.path)
	
	# load stages, but dont slice
	# Handle id/all
	if args.id == "all":
		cprint("#dLoading and slicing stages...#r")

		# create a list of all the hashes and sort by date streamed, slice chronologically
		stagedatas = StageData.load_all_stages(stagedir)
		stagedatas.sort(key=sort_stagedata)

		for stage in stagedatas:
			# Export with ffmpeg
			tmpfile = handle_stage(conf, stagedir, stage)
			# Export chat
			tmpchat = vbchat.process_stage(conf, stage, "export")

			# move appropriate files
			if tmpfile is not None:
				os_replace(tmpfile, args.path / f"{stage.title}.mp4")
			if tmpchat is not None:
				os_replace(tmpchat, args.path / (f"{stage.title}"+tmpchat.suffix))
			
			# deal with old stage
			if conf["stage_export_delete"]:
				os_remove(str(stagedir / f"{stage.id}.stage"))
	else:
		cprint("#dLoading stage...", end=" ")
		
		# check if stage exists, and prep it for slice
		stagedata = StageData.load_from_id(stagedir, args.id)
		
		# Export with ffmpeg
		tmpfile = handle_stage(conf, stagedir, stagedata)
		# Export chat
		tmpchat = vbchat.process_stage(conf, stagedata)

		# move appropriate files
		if tmpfile is not None:
			os_replace(tmpfile, args.path / f"{stagedata.title}.mp4")
		if tmpchat is not None:
			os_replace(tmpchat, args.path / (f"{stagedata.title}"+tmpchat.suffix))
		
		# Deal with old stage
		if conf["stage_export_delete"]:
			os_remove(str(stagedir / f"{stagedata.id}.stage"))

	# say "Done!"
	cprint("#fG#lDone!#r")
