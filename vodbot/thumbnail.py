# based off picauto
# https://gist.github.com/NotQuiteApex/77cdc6c670ec63aff84dd87d672861e5

from .printer import cprint
from .util import has_magick
from .config import Config
from .commands.stage import StageData

import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


# # take in a StageData, process the data given the config, spit out the path to the image
# def generate_thumbnail(conf: Config, stage: StageData) -> Path:
# 	if not has_magick():
# 		cprint("#fY#dWARN: Cannot generate thumbnail, ImageMagick not installed.#r")
# 		return None
	
# 	# to get single frame from a video
# 	# "ffmpeg" "-ss" "<timestamp>" "-i" "<inputvod.mkv>" "-frames:v" "1" "<tmp/screenshot_output.png>"
# 	ss_path = conf.directories.temp / f"thumbnail_ss_{stage.id}.png"
# 	if not stage.thumbnail:
# 		cprint(f"#fY#dWARN: Cannot generate thumbnail, missing thumbnail data for stage `{stage.id}`.#r")
# 		return None
# 	selected_video_slice = stage.thumbnail.video_slice_id
# 	video_slice = stage.slices[selected_video_slice]
# 	subprocess.run([
# 		"ffmpeg", "-ss", stage.thumbnail.timestamp, "-i", video_slice.filepath,
# 		"-frames:v", "1", "-update", "1", str(ss_path), "-y"
# 	], check=True)

# 	# The reference for commands for magick is here:
# 	# https://imagemagick.org/script/magick.php

# 	output_file = conf.directories.temp / f"thumbnail_{stage.id}.png"

# 	cw = conf.thumbnail.canvas_width
# 	ch = conf.thumbnail.canvas_height
# 	ssp = conf.thumbnail.screenshot_pos
# 	cvp = conf.thumbnail.cover_pos
# 	cover_path = conf.directories.thumbnail / conf.thumbnail.cover_filepath

# 	game = conf.thumbnail.games[stage.thumbnail.game]
# 	game_path = conf.directories.thumbnail / game.filepath
# 	gp = conf.thumbnail.game_pos
# 	gs = game.s * gp.s
# 	gx, gy = int(gp.x - ((gp.ox + game.ox) * gs)), int(gp.y - ((gp.oy + game.oy) * gs))

# 	text = stage.thumbnail.text
# 	tp = conf.thumbnail.text_pos
# 	ts = tp.s
# 	tx, ty = int(tp.x - (tp.ox * ts)), int(tp.y - (tp.oy * ts))

# 	# initial
# 	cmds = ["magick", "-size", f"{cw}x{ch}", "canvas:none"]
# 	# font setup
# 	cmds += ["-font", conf.thumbnail.text_font, "-pointsize", conf.thumbnail.text_size]

# 	# screenshot
# 	sss = ssp.s
# 	ssx, ssy = int(ssp.x - (ssp.ox * sss)), int(ssp.x - (ssp.ox * sss))
# 	cmds += ["-draw", f"translate {ssx},{ssy} scale {sss},{sss} image src-over 0,0 0,0 {ss_path}"]
# 	# cover art
# 	cvs = cvp.s
# 	cvx, cvy = int(cvp.x - (cvp.ox * cvs)), int(cvp.x - (cvp.ox * cvs))
# 	cmds += ["-draw", f"translate {cvx},{cvy} scale {cvs},{cvs} image src-over 0,0 0,0 {cover_path}"]
# 	# heads
# 	for i in conf.thumbnail.head_order:
# 		if i >= len(stage.thumbnail.heads):
# 			continue
# 		head = conf.thumbnail.heads[stage.thumbnail.heads[i]]
# 		head_pos = conf.thumbnail.head_positions[i]
# 		head_path = conf.directories.thumbnail / head.filepath
# 		hs = head.s * head_pos.s
# 		hx = int(head_pos.x - ((head_pos.ox + head.ox) * gs))
# 		hy = int(head_pos.y - ((head_pos.ox + head.oy) * gs))
# 		cmds += ["-draw", f"translate {hx},{hy} scale {hs},{hs} image src-over 0,0 0,0 {head_path}"] # head
# 	cmds += ["-draw", f"translate {gx},{gy} scale {gs},{gs} image src-over 0,0 0,0 {game_path}"] # cover
# 	cmds += ["-fill", "white", "-stroke", "black", "-strokewidth", "32", "-draw",
# 		f"gravity NorthWest translate {tx},{ty} scale {ts},{ts} text 0,0 \\'{text}\\'"]
# 	cmds += ["-fill", "white", "-stroke", "width", "-strokewidth", "08", "-draw",
# 		f"gravity NorthWest translate {tx},{ty} scale {ts},{ts} text 0,0 \\'{text}\\'"]
# 	cmds += [output_file]

# 	subprocess.run(cmds, check=True)
	
# 	return output_file


## Experimental pillow-based function
def generate_thumbnail(conf: Config, stage: StageData) -> Path:
	# to get single frame from a video
	# "ffmpeg" "-ss" "<timestamp>" "-i" "<inputvod.mkv>" "-frames:v" "1" "<tmp/screenshot_output.png>"
	ss_path = conf.directories.temp / f"thumbnail_ss_{stage.id}.png"
	if not stage.thumbnail:
		cprint(f"#fY#dWARN: Cannot generate thumbnail, missing thumbnail data for stage `{stage.id}`.#r")
		return None
	selected_video_slice = stage.thumbnail.video_slice_id
	video_slice = stage.slices[selected_video_slice]
	subprocess.run([
		"ffmpeg", "-hide_banner", "-ss", stage.thumbnail.timestamp, "-i", video_slice.filepath,
		"-frames:v", "1", "-update", "1", str(ss_path), "-y", "-loglevel", conf.export.ffmpeg_loglevel
	], check=True)

	output_file = conf.directories.temp / f"thumbnail_{stage.id}.png"

	# setup
	cw = conf.thumbnail.canvas_width
	ch = conf.thumbnail.canvas_height
	tn = Image.new("RGBA", (cw, ch), (0,0,0,0))

	# screenshot
	ssp = conf.thumbnail.screenshot_position
	sss = ssp.s
	ssx, ssy = int(ssp.x - (ssp.ox * sss)), int(ssp.x - (ssp.ox * sss))
	ssi = Image.open(ss_path)
	ssi = ssi.convert("RGBA")
	ssi = ssi.resize((cw, ch), Image.BICUBIC)
	ssi = ssi.resize((int(ssi.size[0]*sss), int(ssi.size[1]*sss)), Image.BICUBIC)
	tn.alpha_composite(ssi, (ssx, ssy))
	ssi.close()

	# cover art
	cvp = conf.thumbnail.cover_position
	cover_path = conf.directories.thumbnail / conf.thumbnail.cover_filepath
	cvs = cvp.s
	cvx, cvy = int(cvp.x - (cvp.ox * cvs)), int(cvp.x - (cvp.ox * cvs))
	cvi = Image.open(cover_path)
	cvi = cvi.convert("RGBA")
	cvi = cvi.resize((cw, ch), Image.BICUBIC)
	cvi = cvi.resize((int(cvi.size[0]*cvs), int(cvi.size[1]*cvs)), Image.BICUBIC)
	tn.alpha_composite(cvi, (cvx, cvy))
	cvi.close()

	# heads
	for i in conf.thumbnail.head_order:
		if i >= len(stage.thumbnail.heads):
			continue
		head = conf.thumbnail.heads[stage.thumbnail.heads[i]]
		head_pos = conf.thumbnail.head_positions[i]
		head_path = conf.directories.thumbnail / head.filepath
		hs = head.s * head_pos.s
		hx = int(head_pos.x - ((head_pos.ox + head.ox) * gs))
		hy = int(head_pos.y - ((head_pos.ox + head.oy) * gs))
		hi = Image.open(head_path)
		hi = hi.convert("RGBA")
		hi = cvi.resize((int(hi.size[0]*hs), int(hi.size[1]*hs)), Image.BICUBIC)
		tn.alpha_composite(hi, (hx, hy))
		hi.close()

	# game
	game = conf.thumbnail.games[stage.thumbnail.game]
	game_path = conf.directories.thumbnail / game.filepath
	gp = conf.thumbnail.game_position
	gs = game.s * gp.s
	gx, gy = int(gp.x - ((gp.ox + game.ox) * gs)), int(gp.y - ((gp.oy + game.oy) * gs))
	gi = Image.open(game_path)
	gi = gi.convert("RGBA")
	gi = gi.resize((int(gi.size[0]*gs), int(gi.size[1]*gs)), Image.BICUBIC)
	tn.alpha_composite(gi, (gx, gy))
	gi.close()

	# text
	fnt = None
	try:
		fnt = ImageFont.truetype(font=conf.thumbnail.text_font, size=conf.thumbnail.text_size)
		text = stage.thumbnail.text
		tp = conf.thumbnail.text_position
		ts = tp.s
		tx, ty = int(tp.x - (tp.ox * ts)), int(tp.y - (tp.oy * ts))
		d = ImageDraw.Draw(tn)
		d.text((tx,ty), text, font=fnt, fill=(255,255,255,255), stroke_width=6, stroke_fill=(0,0,0,255))
		del fnt # close font
	except OSError:
		cprint(f"#fY#dWARN: Cannot find font `{conf.thumbnail.text_font}`, skipping text.#r")

	tn.save(output_file)

	return output_file
