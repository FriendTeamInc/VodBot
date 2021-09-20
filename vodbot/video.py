# Module that manages shelling out commands to ffmpeg, with functions returning paths to the final video.

from . import util
from .printer import cprint
from .commands.stage import StageData, VideoSlice

import os
import subprocess
from pathlib import Path
from typing import List, Tuple


class FailedToSlice(Exception):
	pass

class FailedToConcat(Exception):
	pass

class FailedToCleanUp(Exception):
	pass


def slice_video(TEMP_DIR: Path, vslice: VideoSlice, i: int=0) -> Path:
	tmpfile = TEMP_DIR / f"{vslice.video_id}={i}.mp4"
	cprint(f"#rSlicing stage `#fM{vslice.video_id}#r` #d({vslice.ss} - {vslice.to})#r")

	cmd = [ "ffmpeg", "-ss", vslice.ss ]

	if vslice.to != "EOF":
		cmd += ["-to", vslice.to]

	cmd += [
		"-i", vslice.filename, "-c", "copy",
		str(tmpfile), "-y", "-stats", "-loglevel", "warning"
	]
	
	result = subprocess.run(cmd)

	if result.returncode != 0:
		#cprint(f"#r#fRSkipping stage `{vslice.video_id}` due to error.#r\n")
		raise FailedToSlice
	
	return tmpfile


def concat_video(TEMP_DIR: Path, stage_id: str, slice_paths: List[str]) -> Path:
	# first create file list in temp dir
	list_path = TEMP_DIR / f"concat-{stage_id}.txt"
	with open(str(list_path), "w") as f:
		pass

	# then do subprocess for concat list
	concat_path = TEMP_DIR / f"concat-{stage_id}.mp4"
	cmd = [
		"ffmpeg", "-f", "concat",
		"-safe", "0", "-i", str(list_path),
		"-c", "copy", str(concat_path)
	]
	
	# we need to hop directories real fast to perform this function.
	# we'll come back when we're done.
	cwd = os.getcwd()
	os.chdir(str(TEMP_DIR))

	result = subprocess.run(cmd)

	if result.returncode != 0:
		#cprint(f"#r#fRSkipping stage `{vslice.video_id}` due to error.#r\n")
		raise FailedToConcat

	os.chdir(cwd)

	return concat_path


def process_stage(conf: dict, stage: StageData) -> Tuple[Path]:
	# slice all the slices
	slice_paths = [slice_video(conf, stage.slices[x], x) for x in range(len(stage.slices))]

	# edge case of one video
	if len(slice_paths) == 1:
		return (slice_paths[0], slice_paths)

	# concat all the slices
	concat_path = concat_video(conf, stage.id, slice_paths)

	# clean up old slices
	for path in slice_paths:
		try:
			os.remove(path)
		except Exception as e:
			raise FailedToCleanUp(e)

	# return the path of the concated vid
	return (concat_path, slice_paths)
