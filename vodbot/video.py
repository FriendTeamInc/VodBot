# Module that manages shelling out commands to ffmpeg, with functions returning paths to the final video.

from . import util
from .printer import cprint
from .commands.stage import StageData, VideoSlice

import subprocess
from pathlib import Path
from typing import List, Tuple


class FailedToSlice(Exception):
	pass

class FailedToConcat(Exception):
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


def concat_video(TEMP_DIR: Path, stage_id: str, slice_paths: List[str]):
	# first create file list in temp dir
	with open(str(TEMP_DIR / f""))

	# then do subprocess for concat list

	cmd = [
		"ffmpeg", "-f", "concat",
		"-safe", "0", "-i", "mylist.txt",
		"-c", "copy", "output.mp4"
	]

	return


def process_stage(conf: dict, stage: StageData) -> Tuple[Path]:
	# slice all the slices
	slice_paths = [slice_video(conf, stage.slices[x], x) for x in range(len(stage.slices))]

	# TODO: edge case of one video?

	# concat all the slices
	concat_path = concat_video(conf, stage.id, slice_paths)

	# clean up old slices

	# return the path of the concated vid
	return (concat_path, slice_paths)
