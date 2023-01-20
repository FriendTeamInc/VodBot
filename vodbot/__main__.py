from . import util, __project__, __version__
from .config import DEFAULT_CONFIG_PATH
from .printer import colorize
from .cache import load_cache

import argparse
import argcomplete
from argcomplete.completers import FilesCompleter, DirectoriesCompleter
from pathlib import Path
from importlib import import_module
from requests.exceptions import ConnectionError
from shutil import which


def video_completer(prefix, parsed_args, **kwargs):
	# searches all vod and clip directories for meta files, and strips down the names to just the ID's
	conf = None
	try:
		conf = util.load_conf_wrapper(parsed_args.config)
	except Exception as e:
		argcomplete.warn(f"Failed to open/read/parse VodBot config, `{e}`.")
		return
	
	cache = None
	try:
		cache = load_cache(conf, False, True)
	except Exception as e:
		argcomplete.warn(f"Failed to open/read/parse cache, `{e}`.")
		return

	allvids = []

	for channel in conf.channels:
		login = channel.username

		allvids += [d for d in cache.channels[login].vods if d.startswith(prefix)]
		allvids += [d for d in cache.channels[login].clips if d.startswith(prefix)]
		allvids += [d for d in cache.channels[login].slugs if d.startswith(prefix)]
	
	return allvids


def stage_completer(prefix, parsed_args, **kwargs):
	# searches stage directory for stage files, and strips down the names to just the ID's.
	conf = None
	try:
		conf = util.load_conf_wrapper(parsed_args.config)
	except Exception as e:
		argcomplete.warn(f"Failed to open/read/parse VodBot config, `{e}`.")
		return

	cache = None
	try:
		cache = load_cache(conf, False, True)
	except Exception as e:
		argcomplete.warn(f"Failed to open/read/parse cache, `{e}`.")
		return

	stages = [d for d in cache.stages if d.startswith(prefix)]

	cmd = parsed_args.cmd
	pushload = cmd == "push" or cmd == "upload"

	addall = []
	if (pushload or cmd == "export") and "all".startswith(prefix):
		addall = ["all"]

	addlogout = []
	if pushload and "logout".startswith(prefix):
		addlogout = ["logout"]

	addlogin = []
	if pushload and "login".startswith(prefix):
		addlogin = ["login"]
	
	return stages + addall + addlogout + addlogin


def deffered_main():
	# Catch KeyboardInterrupts or connection failures, and report them cleanly
	try:
		main()
	except ConnectionError:
		util.exit_prog(-2, "Failed to connect to the Internet/Intranet/ARPAnet/etc.")
	except KeyboardInterrupt:
		util.exit_prog(-1, "Interrupted by user.")


def main():
	titletext = colorize(f'#fM* {__project__} {__version__} (c) 2020-23 Logan "NotQuiteApex" Hickok-Dickson & Friend Team Inc. *#r')

	# Process arguments
	parser = argparse.ArgumentParser(description="Downloads and processes VODs and clips from Twitch.tv channels.")
	parser.add_argument("-v","--version", action="version", version=titletext)
	parser.add_argument("-n", "--no-color", action="store_true", dest="color_toggle", default=False,
		help="disables colorful output of the program")
	parser.add_argument("-u", "--update-cache", action="store_true", dest="cache_toggle", default=False,
		help="updates the local cache with ID's of users, VODs, and Clips")
	parser.add_argument("-c","--config", type=Path, dest="config", metavar="CFG", default=DEFAULT_CONFIG_PATH,
		help="location of the config file to use").completer = FilesCompleter

	# Subparsers for different commands
	subparsers = parser.add_subparsers(title="command", dest="cmd", metavar="CMD",
		help="command to run: init, info, pull, stage, or upload.")

	# `vodbot init`
	initparse = subparsers.add_parser("init", description="Runs the setup process for VodBot")
	initparse.add_argument("-o", "--output", type=Path, default=DEFAULT_CONFIG_PATH, dest="output", metavar="PATH",
		help="path to save the config to").completer = FilesCompleter

	# `vodbot pull <vods/clips/both>`
	download = subparsers.add_parser("pull", aliases=["pull", "download"], description="Downloads VODs and/or clips.")
	download.add_argument("type", type=str, default="both", nargs="?", choices=("vods", "clips", "both"),
		help='what type of content to pull, can be "vods", "clips", or "both"')

	# `vodbot stage`
	stager = subparsers.add_parser("stage",
		description="Stages sections of video to upload or export",)
	stager_subparser = stager.add_subparsers(title="action", dest="action", metavar="ACT",
		description='action for video stages: new, list, or rm.')

	# `vodbot stage new \`
	# `<some_id> [--ss "0:0:0"] [--to "0:59:59"] <other_id> [--ss "0:20:0"] [--to "2:59:06"] \`
	# `<other_id> [--ss "3:20:0"] [--to "4:59:06"] <also_id> [--ss "0:40:0"] [--to "6:59:59"] \`
	# `[--streamer notquiteapex] [--streamer percy_creates]`
	# `[--title "Apex + Percy - Minecraft (Part 5)"] [--desc "PogChamp {streamer}\n{link}"] \`
	# `[--thumbnail-head notquiteapex] [--thumbnail-head percy_creates] \`
	# `[--thumbnail-game minecraft] [--thumbnail-text "#5"] \`
	# `[--thumbnail-video-id 1] [--thumbnail-timestamp "3:50:05"]`
	stager_add = stager_subparser.add_parser("new", description="creates a new stage for videos and clips to be mixed")
	stager_add.add_argument("id", help="id of the VOD or Clip to stage", type=str, nargs="+").completer = video_completer
	stager_add.add_argument("--streamer", help="a streamer of the video (listable)", type=str, default=[], nargs="?", action="append", metavar="USER")
	stager_add.add_argument("--title", help="title of finished video", type=str, default="")
	stager_add.add_argument("--desc", help="description of finished video", type=str, default="")
	stager_add.add_argument("--ss", help="start time of video (listable)", type=str, default=[], nargs="?", action="append")
	stager_add.add_argument("--to", help="end time of video (listable)", type=str, default=[], nargs="?", action="append")
	stager_add.add_argument("--tn-head", help="head for the thumbnail (listable)", type=str, default=[], nargs="?", action="append", metavar="HEAD")
	stager_add.add_argument("--tn-game", help="game for the thumbnail", type=str, default="", metavar="GAME")
	stager_add.add_argument("--tn-text", help="text for the thumbnail", type=str, default="", metavar="TEXT")
	stager_add.add_argument("--tn-video-id", help="video id (index) for the thumbnail screenshot", type=str, default="", metavar="IDX")
	stager_add.add_argument("--tn-timestamp", help="timestamp for the thumbnail screenshot", type=str, default="", metavar="TIMESTAMP")

	# `vodbot stage rm <id>`
	stager_rm = stager_subparser.add_parser("rm", description="removes a VOD or Clip from the staging area")
	stager_rm.add_argument("id", type=str, help="id of the staged video data").completer = stage_completer

	# `vodbot stage list [id]`
	stager_list = stager_subparser.add_parser("list", description="lists info on staging area or staged items")
	stager_list.add_argument("id", type=str, help="id of the staged video data",
		nargs="?", default=None).completer = stage_completer

	# `vodbot upload <stage_id/all>`
	upload = subparsers.add_parser("push", aliases=["push", "upload"], description="Uploads stage(s) to YouTube.")
	# TODO: update with login for #60
	upload.add_argument("id", type=str,
		help='id of the staged video data, "all" to upload all stages, "login" to add YouTube credentials, '
			'or "logout" to remove existing YouTube credentials').completer = stage_completer
	
	# `vodbot export <stage_id/all>`
	export = subparsers.add_parser("export", aliases=["export", "slice"], description="Uploads stage(s) to YouTube.")
	export.add_argument("id", type=str, help="id of the staged video data, or `all` for all stages").completer = stage_completer
	export.add_argument("path", type=Path, help="directory to export the video(s) to").completer = DirectoriesCompleter

	# `vodbot info <vod/clip/channel_id/url>`
	info = subparsers.add_parser("info", description="Prints out info on the Channel, Clip, or VOD given.")
	info.add_argument("id", type=str, help="id/url of the Channel, Clip, or VOD")
	
	argcomplete.autocomplete(parser)
	args = parser.parse_args()

	# Check for ffmpeg
	ffmpeg_check = which("ffmpeg")
	if ffmpeg_check is None:
		util.exit_prog(-11, "FFmpeg could not be found in your PATH environment variable.")

	# Handle commands
	if args.cmd == "init":
		import_module(".commands.init", "vodbot").run(args)
	elif args.cmd == "pull" or args.cmd == "download":
		import_module(".commands.pull", "vodbot").run(args)
	elif args.cmd == "stage":
		import_module(".commands.stage", "vodbot").run(args)
	elif args.cmd == "push" or args.cmd == "upload":
		import_module(".commands.upload", "vodbot").run(args)
	elif args.cmd == "export" or args.cmd == "slice":
		import_module(".commands.export", "vodbot").run(args)
	elif args.cmd == "info":
		import_module(".commands.info", "vodbot").run(args)
	else:
		util.exit_prog(-3, f"Unknown top-level command `{args.cmd}`, run with `-h` to see what commands are available.")


if __name__ == "__main__":
	deffered_main()
