from . import util, __project__, __version__
from .printer import colorize

import argparse
from pathlib import Path
from importlib import import_module
from requests.exceptions import ConnectionError


# Default path
vodbotdir = util.vodbotdir


def deffered_main():
	# Catch KeyboardInterrupts or connection failures, and report them cleanly
	try:
		main()
	except ConnectionError:
		util.exit_prog(-2, "Failed to connect to Twitch.")
	except KeyboardInterrupt:
		util.exit_prog(-1, "Interrupted by user.")


def main():
	titletext = colorize('#r#fM#l* {} {} (c) 2020-21 Logan "NotQuiteApex" Hickok-Dickson *#r')
	titletext = titletext.format(__project__, __version__)
	
	print(titletext)

	# Process arguments
	parser = argparse.ArgumentParser(epilog=titletext,
		description="Downloads and processes VODs and clips from Twitch.tv channels.")
	parser.add_argument("-v","--version", action="version", version=titletext)
	parser.add_argument("-c","--config", type=Path, dest="config",
		help="location of the Twitch config file to use", default=util.DEFAULT_CONF_PATH)

	# Subparsers for different commands
	subparsers = parser.add_subparsers(title="command", dest="cmd", help="command to run.")

	# `vodbot init`
	initparse = subparsers.add_parser("init", epilog=titletext,
		description="Runs the setup process for VodBot")
	initparse.add_argument("--output", help="path to save the config to; defaults to ~/.vodbot/conf.json",
		type=Path, required=False, default=util.DEFAULT_CONF_PATH, dest="output", metavar="PATH")
	initparse.add_argument("--default", action="store_true",
		help="argument switch to write default config; overrides all subsequent options")
	initparse.add_argument("--channels", type=str, default=[], nargs="+",
		help="twitch.tv channel login to pull VODs/Clips from", metavar="CHL")
	initparse.add_argument("--timezone", type=str, required=False, default=None,
		help="timezone for datetime referencing, as a UTC string")
	initparse.add_argument("--vod-dir", help="absolute path to store VOD data",
		type=Path, required=False, default=None, dest="voddir", metavar="PATH")
	initparse.add_argument("--clip-dir", help="absolute path to store Clip data",
		type=Path, required=False, default=None, dest="clipdir", metavar="PATH")
	initparse.add_argument("--temp-dir", help="absolute path to store temporary data",
		type=Path, required=False, default=None, dest="tempdir", metavar="PATH")
	initparse.add_argument("--stage-dir", help="absolute path to store staged data",
		type=Path, required=False, default=None, dest="stagedir", metavar="PATH")

	# `vodbot pull <vods/clips/both> [channel ...]`
	download = subparsers.add_parser("download", aliases=["pull", "download"],
		epilog=titletext, description="Downloads VODs and/or clips.")
	download.add_argument("type", type=str, default="both", nargs="?",
		help='content type flag, can be "vods", "clips", or "both"; defaults to "both"')
	download.add_argument("channels", metavar="channel", type=str, default=[], nargs="*",
		help="twitch.tv channel name to pull VODs from; optional, defaults to config")

	# `vodbot stage`
	stager = subparsers.add_parser("stage", epilog=titletext,
		description="Stages sections of video to upload or export",)
	stager_subparser = stager.add_subparsers(title="action", dest="action",
		description='action for staging the video')

	# `vodbot stage new \
	# `[--title "Apex - BBT"] [--desc "PogChamp {streamer}\n{link}"] \`
	# `<some_id> [--ss "0:0:0"] [--to "0:59:59"] \`
	# `<other_id> [--ss "0:20:0"] [--to "2:59:06"] \`
	# `<other_id> [--ss "3:20:0"] [--to "4:59:06"] \`
	# `<also_id> [--ss "0:40:0"] [--to "6:59:59"]`
	stager_add = stager_subparser.add_parser("new", epilog=titletext,
		description="creates a new stage for videos and clips to be mixed")
	stager_add.add_argument("id", help="id of the VOD or Clip to stage",
		type=str, nargs="+")
	stager_add.add_argument("--title", help="title of finished video",
		type=str, required=False, default="")
	stager_add.add_argument("--desc", help="description of finished video",
		type=str, required=False, default="")
	stager_add.add_argument("--ss", help="start time of video",
		type=str, required=False, default=[], nargs="?", action="append")
	stager_add.add_argument("--to", help="end time of video",
		type=str, required=False, default=[], nargs="?", action="append")

	# `vodbot stage rm <id>`
	stager_rm = stager_subparser.add_parser("rm", epilog=titletext,
		description="removes a VOD or Clip from the staging area")
	stager_rm.add_argument("id", type=str, help="id of the staged video data")

	# `vodbot stage list [id]`
	stager_list = stager_subparser.add_parser("list", epilog=titletext,
		description="lists info on staging area or staged items")
	stager_list.add_argument("id", nargs="?", type=str, help="id of the staged video data", default=None)

	# `vodbot upload <id/all>`
	upload = subparsers.add_parser("upload", aliases=["upload", "push"],
		epilog=titletext, description="Uploads stage(s) to YouTube.")
	upload.add_argument("id", type=str,
		help='id of the staged video data, "all" to upload all stages, or "logout" to remove existing YouTube credentials')
	
	# `vodbot export <id/all>`
	export = subparsers.add_parser("export", aliases=["export", "slice"],
		epilog=titletext, description="Uploads stage(s) to YouTube.")
	export.add_argument("id", type=str, help="id of the staged video data, or `all` for all stages")
	export.add_argument("path", type=Path, help="directory to export the video(s) to")

	# `vodbot upload <id/all>`
	info = subparsers.add_parser("info", epilog=titletext,
		description="Prints out info on the Channel, Clip, or VOD given.")
	info.add_argument("id", type=str, help="id/url of the Channel, Clip, or VOD")
	
	args = parser.parse_args()

	# Handle commands
	if args.cmd == "init":
		init = import_module(".commands.init", "vodbot")
		init.run(args)
	elif args.cmd == "pull" or args.cmd == "download":
		pull = import_module(".commands.pull", "vodbot")
		pull.run(args)
	elif args.cmd == "stage":
		stage = import_module(".commands.stage", "vodbot")
		stage.run(args)
	elif args.cmd == "upload" or args.cmd == "push":
		upload = import_module(".commands.upload", "vodbot")
		upload.run(args)
	elif args.cmd == "export" or args.cmd == "slice":
		export = import_module(".commands.export", "vodbot")
		export.run(args)
	elif args.cmd == "info":
		info = import_module(".commands.info", "vodbot")
		info.run(args)


if __name__ == "__main__":
	deffered_main()
