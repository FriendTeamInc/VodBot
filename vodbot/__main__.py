from . import util, __project__, __version__
from .config import DEFAULT_CONFIG_PATH, DEFAULT_CONFIG

import argparse
from pathlib import Path
from importlib import import_module
from requests.exceptions import ConnectionError


def deffered_main():
	# Catch KeyboardInterrupts or connection failures, and report them cleanly
	try:
		main()
	except ConnectionError:
		util.exit_prog(-2, "Failed to connect to the Internet/Intranet/ARPAnet/etc.")
	except KeyboardInterrupt:
		util.exit_prog(-1, "Interrupted by user.")


def main():
	titletext = f'* {__project__} {__version__} (c) 2020-22 Logan "NotQuiteApex" Hickok-Dickson *'

	#print(type(DEFAULT_CONFIG.directories.clips))

	# Process arguments
	parser = argparse.ArgumentParser(description="Downloads and processes VODs and clips from Twitch.tv channels.")
	parser.add_argument("-v","--version", action="version", version=titletext)
	parser.add_argument("-c","--config", type=Path, dest="config", default=DEFAULT_CONFIG_PATH,
		help="location of the Twitch config file to use")
	parser.add_argument("-n", "--no-color", action="store_true", dest="color_toggle", default=False,
		help="disables colorful output of the program")

	# Subparsers for different commands
	subparsers = parser.add_subparsers(title="command", dest="cmd", help="command to run.")

	# `vodbot init`
	initparse = subparsers.add_parser("init", description="Runs the setup process for VodBot")
	initparse.add_argument("-o", "--output", type=Path, default=DEFAULT_CONFIG_PATH, dest="output", metavar="PATH",
		help="path to save the config to")

	# `vodbot pull <vods/clips/both>`
	download = subparsers.add_parser("pull", description="Downloads VODs and/or clips.")
	download.add_argument("type", type=str, default="both", nargs="?",
		help='content type flag, can be "vods", "clips", or "both"')

	# `vodbot stage`
	stager = subparsers.add_parser("stage",
		description="Stages sections of video to upload or export",)
	stager_subparser = stager.add_subparsers(title="action", dest="action",
		description='action for staging the video')

	# `vodbot stage new \
	# `[--title "Apex - BBT"] [--desc "PogChamp {streamer}\n{link}"] \`
	# `<some_id> [--ss "0:0:0"] [--to "0:59:59"] \`
	# `<other_id> [--ss "0:20:0"] [--to "2:59:06"] \`
	# `<other_id> [--ss "3:20:0"] [--to "4:59:06"] \`
	# `<also_id> [--ss "0:40:0"] [--to "6:59:59"]`
	stager_add = stager_subparser.add_parser("new", description="creates a new stage for videos and clips to be mixed")
	stager_add.add_argument("id", help="id of the VOD or Clip to stage", type=str, nargs="+")
	stager_add.add_argument("--title", help="title of finished video", type=str, default="")
	stager_add.add_argument("--desc", help="description of finished video", type=str, default="")
	stager_add.add_argument("--ss", help="start time of video", type=str, default=[], nargs="?", action="append")
	stager_add.add_argument("--to", help="end time of video", type=str, default=[], nargs="?", action="append")

	# `vodbot stage rm <id>`
	stager_rm = stager_subparser.add_parser("rm", description="removes a VOD or Clip from the staging area")
	stager_rm.add_argument("id", type=str, help="id of the staged video data")

	# `vodbot stage list [id]`
	stager_list = stager_subparser.add_parser("list", description="lists info on staging area or staged items")
	stager_list.add_argument("id", nargs="?", type=str, help="id of the staged video data", default=None)

	# `vodbot upload <stage_id/all>`
	upload = subparsers.add_parser("push", description="Uploads stage(s) to YouTube.")
	upload.add_argument("id", type=str,
		help='id of the staged video data, "all" to upload all stages, or "logout" to remove existing YouTube credentials')
	
	# `vodbot export <stage_id/all>`
	export = subparsers.add_parser("export", description="Uploads stage(s) to YouTube.")
	export.add_argument("id", type=str, help="id of the staged video data, or `all` for all stages")
	export.add_argument("path", type=Path, help="directory to export the video(s) to")

	# `vodbot info <vod/clip/channel_id/url>`
	info = subparsers.add_parser("info", description="Prints out info on the Channel, Clip, or VOD given.")
	info.add_argument("id", type=str, help="id/url of the Channel, Clip, or VOD")
	
	args = parser.parse_args()

	# Handle commands
	if args.cmd == "init":
		import_module(".commands.init", "vodbot").run(args)
	elif args.cmd == "pull":
		import_module(".commands.pull", "vodbot").run(args)
	elif args.cmd == "stage":
		import_module(".commands.stage", "vodbot").run(args)
	elif args.cmd == "push":
		import_module(".commands.upload", "vodbot").run(args)
	elif args.cmd == "export":
		import_module(".commands.export", "vodbot").run(args)
	elif args.cmd == "info":
		import_module(".commands.info", "vodbot").run(args)
	else:
		print(titletext)
		print("* run with `-h` to find what commands are available *")


if __name__ == "__main__":
	deffered_main()
