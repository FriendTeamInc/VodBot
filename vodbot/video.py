# Module that manages shelling out commands to ffmpeg, with functions returning paths to the final video.

from . import util
from .printer import cprint
from .commands.stage import StageData, VideoSlice

import os
import subprocess
from pathlib import Path
from typing import List, Tuple


class VideoFailure(Exception):
	def __init__(self, vid="?") -> None:
		self.vid = vid
		super().__init__(self.vid)

class FailedToSlice(VideoFailure):
	pass

class FailedToConcat(VideoFailure):
	pass

class FailedToCleanUp(VideoFailure):
	pass


def slice_video(TEMP_DIR: Path, LOG_LEVEL: str, vslice: VideoSlice, i: int=0) -> Path:
	tmpfile = TEMP_DIR / f"{vslice.video_id}={i}.mp4"
	cprint(f"#rSlicing stage `#fM{vslice.video_id}#r` #d({vslice.ss} - {vslice.to})#r")

	cmd = [ "ffmpeg", "-hide_banner", "-ss", vslice.ss ]

	if vslice.to != "EOF":
		cmd += ["-to", vslice.to]

	cmd += [
		"-i", vslice.filepath, "-c", "copy",
		str(tmpfile), "-y", "-stats", "-loglevel", LOG_LEVEL
	]
	
	result = subprocess.run(cmd)

	if result.returncode != 0:
		raise FailedToSlice(vslice.video_id)
	
	return tmpfile


def concat_video(TEMP_DIR: Path, LOG_LEVEL: str, stage_id: str, slice_paths: List[Path]) -> Path:
	# first create file list in temp dir
	list_path = TEMP_DIR / f"concat-{stage_id}.txt"
	with open(str(list_path), "w") as f:
		for path in slice_paths:
			f.write(f"file '{path.name}'\n")

	# then do subprocess for concat list
	concat_path = TEMP_DIR / f"concat-{stage_id}.mp4"
	cmd = [
		"ffmpeg", "-hide_banner", "-f", "concat",
		"-safe", "0", "-i", str(list_path),
		"-c", "copy", str(concat_path),
		"-y", "-stats", "-loglevel", LOG_LEVEL
	]
	
	print()
	cprint(f"#rConcatentating videos for `#fM{stage_id}#r`")
	
	# we need to hop directories real fast to perform this function.
	# we'll come back when we're done.
	cwd = os.getcwd()
	os.chdir(str(TEMP_DIR))

	result = subprocess.run(cmd)

	if result.returncode != 0:
		raise FailedToConcat()

	os.chdir(cwd)

	cprint(f"Cleaning up after stage `#fM{stage_id}#r`...")

	try:
		os.remove(str(list_path))
	except Exception as e:
		raise FailedToCleanUp(e)

	return concat_path


def process_stage(conf: dict, stage: StageData) -> Path:
	tempdir = Path(conf["temp_dir"])
	loglevel = conf["ffmpeg_loglevel"]

	# slice all the slices
	slice_paths = [slice_video(tempdir, loglevel, stage.slices[x], x) for x in range(len(stage.slices))]

	# edge case of one video
	if len(slice_paths) == 1:
		return slice_paths[0]

	# concat all the slices
	concat_path = concat_video(tempdir, loglevel, stage.id, slice_paths)

	# clean up old slices
	for path in slice_paths:
		try:
			os.remove(path)
		except Exception as e:
			raise FailedToCleanUp(e)

	# return the path of the concated vid
	return concat_path
