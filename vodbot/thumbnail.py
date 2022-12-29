# based off picauto
# https://gist.github.com/NotQuiteApex/77cdc6c670ec63aff84dd87d672861e5

from .config import Config
from .commands.stage import StageData

import subprocess
from pathlib import Path


# take in a StageData, process the data given the config, spit out the path to the image
def generate_thumbnail(conf: Config, stage: StageData) -> Path:
	# to get single frame from a video
	# "ffmpeg" "-ss" "<timestamp>" "-i" "<inputvod.mkv>" "-frames:v" "1" "<tmp/screenshot_output.png>"
	thumbnail_filename = conf.directories.temp / f"thumbnail_ss_{stage.id}.png"
	selected_video_slice = stage.thumbnail.video_slice_id
	video_slice = stage.slices[selected_video_slice]
	subprocess.run([
		"ffmpeg", "-ss", stage.thumbnail.timestamp, "-i", video_slice.filepath,
		"-frames:v", "1", str(thumbnail_filename)
	], check=True)

	# to generate a thumbnail with imagemagick
	# notes: tx and ty are generated with pos-(offset*scale), s is scale
	# initial: "magick" "-size" "<canvas_width>x<canvas_height>" "canvas:none" "-font" "<text_font>" "-pointsize" "<text_size>"
	# screenshot: "-draw" "image src-over <screenshot_x>,<screenshot_y> <canvas_width>,<canvas_height> \\'<tmp/screenshot_output.png>\\'"
	# cover image: "-draw" "image src-over <cover_x>,<cover_y> <canvas_width>,<canvas_height> \\'<thumbnail/cover.png>\\'"
	# loop over positions and heads: "-draw" "translate <tx>,<ty> scale <s>,<s> image src-over 0,0 0,0 \\'<thumbnail/heads/head.png>\\'"
	# game image: "-draw" "translate <tx>,<ty> scale <s>,<s> image src-over 0,0 0,0 \\'<thumbnail/games/game.png>\\'"
	# text: "-fill" "white" "-stroke" "black" "-strokewidth" "32" "-draw" "gravity NorthWest text <text_x>,<text_y> \\'<textTEXT>\\'"
	# text: "-fill" "white" "-stroke" "white" "-strokewidth" "08" "-draw" "gravity NorthWest text <text_x>,<text_y> \\'<textTEXT>\\'"
	# output: "<tmp/out.png>"
	output_file = conf.directories.temp / f"thumbnail_{stage.id}.png"

	cv_x = conf.thumbnail.canvas_width
	cv_y = conf.thumbnail.canvas_height
	ss_x = conf.thumbnail.screenshot_x
	ss_y = conf.thumbnail.screenshot_y
	cover_path = conf.directories.thumbnail / conf.thumbnail.cover_filepath
	fg_x = conf.thumbnail.cover_x
	fg_y = conf.thumbnail.cover_y

	game = conf.thumbnail.games[stage.thumbnail.game]
	game_path = conf.directories.thumbnail / game.filepath
	gs = game.scale
	gx = int(conf.thumbnail.game_x - (game.offset_x * gs))
	gy = int(conf.thumbnail.game_y - (game.offset_y * gs))

	text = stage.thumbnail.text
	tx = conf.thumbnail.text_x
	ty = conf.thumbnail.text_y

	cmds = ["magick", "-size", f"{cv_x}x{cv_y}", "canvas:none"] # initial
	cmds += ["-font", conf.thumbnail.text_font, "-pointsize", conf.thumbnail.text_size] # font
	cmds += ["-draw", f"image src-over {ss_x},{ss_y} {cv_x},{cv_y} {thumbnail_filename}"] # screenshot
	cmds += ["-draw", f"image src-over {fg_x},{fg_y} {cv_x},{cv_y} {cover_path}"] # cover
	# heads
	for i in conf.thumbnail.head_order:
		if i >= len(stage.thumbnail.heads):
			continue
		head = conf.thumbnail.heads[stage.thumbnail.heads[i]]
		head_pos = conf.thumbnail.head_positions[i]
		head_path = conf.directories.thumbnail / head.filepath
		hs = head.scale * head_pos.scale
		hx = int(head_pos.x - (head.offset_x * gs))
		hy = int(head_pos.y - (head.offset_y * gs))
		cmds += ["-draw", f"translate {hx},{hy} scale {hs},{hs} image src-over 0,0 0,0 {head_path}"] # head
	cmds += ["-draw", f"translate {gx},{gy} scale {gs},{gs} image src-over 0,0 0,0 {game_path}"] # cover
	cmds += ["-fill", "white", "-stroke", "black", "-strokewidth", "32", "-draw", f"gravity NorthWest text {tx},{ty} \\'{text}\\'"]
	cmds += ["-fill", "white", "-stroke", "width", "-strokewidth", "08", "-draw", f"gravity NorthWest text {tx},{ty} \\'{text}\\'"]
	cmds += [output_file]

	subprocess.run(cmds, check=True)
	
	return output_file
