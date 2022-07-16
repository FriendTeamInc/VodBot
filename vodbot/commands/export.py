# Export video data to a specific location

from .stage import StageData

import vodbot.util as util
import vodbot.video as vbvid
import vodbot.chatlog as vbchat

from datetime import datetime
from pathlib import Path
from os import remove as os_remove, replace as os_replace


# Default path
vodbotdir = util.vodbotdir
stagedir = None


DISALLOWED_CHARACTERS = [
	"/", "\\", "<", ">", ":",
	"\"", "|", "?", "*"
]


EPOCH = datetime.utcfromtimestamp(0)
def sort_stagedata(stagedata):
	date = datetime.strptime(stagedata.datestring, "%Y/%m/%d")
	return (date - EPOCH).total_seconds()


def handle_stage(conf: dict, stage: StageData) -> Path:
	tmpfile = None
	try:
		tmpfile = vbvid.process_stage(conf, stage)
	except vbvid.FailedToSlice as e:
		print(f"Skipping stage `{stage.id}`, failed to slice video with ID of `{e.vid}`.\n")
		return None
	except vbvid.FailedToConcat:
		print(f"Skipping stage `{stage.id}`, failed to concatenate videos.\n")
		return None
	except vbvid.FailedToCleanUp as e:
		print(f"Skipping stage `{stage.id}`, failed to clean up temp files.\n\n{e.vid}")
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
		print("Loading and slicing stages...")

		# create a list of all the hashes and sort by date streamed, slice chronologically
		stagedatas = StageData.load_all_stages(stagedir)
		stagedatas.sort(key=sort_stagedata)

		for stage in stagedatas:
			tmpfile = None
			tmpchat = None
			# Export with ffmpeg
			tmpfile = handle_stage(conf, stage)
			# Export chat
			tmpchat = vbchat.process_stage(conf, stage, "export")

			title = stage.title.strip()
			for x in DISALLOWED_CHARACTERS:
				title = title.replace(x, "_")

			# move appropriate files
			if tmpfile is not None:
				os_replace(tmpfile, args.path / (title+tmpfile.suffix))
			if tmpchat is not None:
				os_replace(tmpchat, args.path / (title+tmpchat.suffix))
			
			# deal with old stage
			if conf["stage_export_delete"]:
				os_remove(str(stagedir / f"{stage.id}.stage"))
	else:
		print("Loading stage...", end=" ")
		
		# check if stage exists, and prep it for slice
		stagedata = StageData.load_from_id(stagedir, args.id)
		
		tmpfile = None
		tmpchat = None
		
		# Export with ffmpeg
		tmpfile = handle_stage(conf, stagedata)
		# Export chat
		tmpchat = vbchat.process_stage(conf, stagedata, "export")
		
		title = stagedata.title.strip()
		for x in DISALLOWED_CHARACTERS:
			title = title.replace(x, "_")

		# move appropriate files
		if tmpfile is not None:
			os_replace(tmpfile, args.path / (title+tmpfile.suffix))
		if tmpchat is not None:
			os_replace(tmpchat, args.path / (title+tmpchat.suffix))
		
		# Deal with old stage
		if conf["stage_export_delete"]:
			os_remove(str(stagedir / f"{stagedata.id}.stage"))

	# say "Done!"
	print("Done!")
