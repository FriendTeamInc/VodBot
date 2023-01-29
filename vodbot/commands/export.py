# Export video data to a specific location

from vodbot.webhook import send_export_error, send_export_job_done, send_export_video
from .stage import StageData

import vodbot.util as util
import vodbot.video as vbvid
import vodbot.chatlog as vbchat
import vodbot.thumbnail as vbthumbnail
from vodbot.config import Config
from vodbot.printer import cprint
from vodbot.cache import load_cache, save_cache

from datetime import datetime
from pathlib import Path
from os import remove as os_remove
from shutil import move as shutil_move


DISALLOWED_CHARACTERS = [
	"/", "\\", "<", ">", ":",
	"\"", "|", "?", "*"
]


EPOCH = datetime.utcfromtimestamp(0)
def sort_stagedata(stagedata):
	date = datetime.strptime(stagedata.datestring, "%Y/%m/%d")
	return (date - EPOCH).total_seconds()


def handle_stage(conf: Config, stage: StageData) -> Path:
	tmpfile = None
	try:
		tmpfile = vbvid.process_stage(conf, stage)
	except vbvid.FailedToSlice as e:
		cprint(f"#r#fRSkipping stage `{stage.id}`, failed to slice video with ID of `{e.video_id}`.#r\n")
		send_export_error(f'For stage "{stage.id}", failed to slice video with ID "{e.video_id}".')
		return None
	except vbvid.FailedToConcat:
		cprint(f"#r#fRSkipping stage `{stage.id}`, failed to concatenate videos.#r\n")
		send_export_error(f'For stage "{stage.id}", failed to concatenate videos.')
		return None
	except vbvid.FailedToCleanUp as e:
		cprint(f"#r#fRSkipping stage `{stage.id}`, failed to clean up temporary files.#r\n\n{e.vid}")
		send_export_error(f'For stage "{stage.id}", failed to clean up temporary files.')
		return None
	
	return tmpfile


def run(args):
	conf = util.load_conf(args.config)
	cache = load_cache(conf, args.cache_toggle)
	STAGE_DIR = conf.directories.stage

	util.make_dir(args.path)
	args.path = Path(args.path)
	
	# load stages, but dont slice
	# Handle id/all
	cprint("#dLoading and slicing stages...#r", flush=True)
	stagedatas = []
	if args.id == "all":
		stagedatas = StageData.load_all_stages(STAGE_DIR)
		stagedatas.sort(key=sort_stagedata)
	else:
		stagedatas = [StageData.load_from_id(STAGE_DIR, args.id)]
	
	fin_vids = 0
	for stage in stagedatas:
		tmpfile = None
		tmpchat = None
		tmpnail = None
		# Export with FFmpeg
		if conf.export.video_enable:
			tmpfile = handle_stage(conf, stage)
		# Export chat
		if conf.export.chat_enable:
			tmpchat = vbchat.process_stage(conf, stage, "export")
		# Export thumbnail
		if conf.export.thumbnail_enable:
			tmpnail = vbthumbnail.generate_thumbnail(conf, stage)

		title = stage.title.strip()
		for x in DISALLOWED_CHARACTERS:
			title = title.replace(x, "_")

		# move appropriate files
		if tmpfile is not None:
			shutil_move(str(tmpfile), str(args.path / (title+tmpfile.suffix)))
		if tmpchat is not None:
			shutil_move(str(tmpchat), str(args.path / (title+tmpchat.suffix)))
		if tmpnail is not None:
			shutil_move(str(tmpnail), str(args.path / (title+tmpnail.suffix)))
		
		# deal with old stage
		if conf.stage.delete_on_export:
			os_remove(STAGE_DIR / f"{stage.id}.stage")
			cache.stages.remove(stage.id)
			save_cache(conf, cache)

		fin_vids += 1
		send_export_video(stage)
	
	# say "Done!"
	# cprint("#fG#lDone!#r")
	send_export_job_done(fin_vids, len(stagedatas))
