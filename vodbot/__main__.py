from . import util, __project__, __version__
from .printer import cprint, colorize

import argparse
from os.path import exists
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
	titletext = colorize('#r#fM#l* VodBot {} (c) 2020-21 Logan "NotQuiteApex" Hickok-Dickson *#r')
	titletext = titletext.format(__version__)

	# Process arguments
	parser = argparse.ArgumentParser(epilog=titletext,
		description="Downloads and processes VODs and clips from Twitch.tv channels.")
	parser.add_argument("-v","--version", action="version", version=titletext)
	parser.add_argument("-c", type=str, dest="config",
		help="location of the Twitch config file",
		default=str(vodbotdir / "conf.json"))

	# Subparsers for different commands
	subparsers = parser.add_subparsers(title="command", dest="cmd", help="command to run.")

	# `vodbot init`
	initparse = subparsers.add_parser("init", epilog=titletext,
		description="Runs the setup process for VodBot")

	# `vodbot pull <vods/clips/both> [channel ...]`
	download = subparsers.add_parser("pull", epilog=titletext,
		description="Downloads VODs and/or clips.")
	download.add_argument("type", type=str, default="both", nargs="?",
		help='content type flag, can be "vods", "clips", or "both"; defaults to "both"')
	download.add_argument("channels", metavar="channel", type=str, default=[], nargs="*",
		help="twitch.tv channel name to pull VODs from; optional, defaults to config")

	# `vodbot stage`
	stager = subparsers.add_parser("stage", epilog=titletext,
		description="Stages sections of video to upload",)
	stager_subparser = stager.add_subparsers(title="action", dest="action",
		description='action for staging the video')
	# `vodbot stage add <id> [--ss="0:0:0"] [--to="99:59:59"] \`
	# `[--title="Apex - BBT"] [--desc="PogChamp {streamer}\n{link}"]`
	stager_add = stager_subparser.add_parser("add", epilog=titletext,
		description="adds a VOD or Clip to the staging area")
	stager_add.add_argument("id", type=str, help="id of the VOD or Clip to stage")
	stager_add.add_argument("--title", help="title of video", type=str, required=False, default="")
	stager_add.add_argument("--ss", help="start time of video", type=str, required=False, default="")
	stager_add.add_argument("--to", help="end time of video", type=str, required=False, default="")
	stager_add.add_argument("--desc", help="description of video", type=str, required=False, default="")
	# `vodbot stage rm <id>`
	stager_rm = stager_subparser.add_parser("rm", epilog=titletext,
		description="removes a VOD or Clip from the staging area")
	stager_rm.add_argument("id", type=str, help="id of the staged video data")
	# `vodbot stage edit <id>`
	stager_rm = stager_subparser.add_parser("edit", epilog=titletext,
		description="edits data of a VOD or Clip in the staging area")
	stager_rm.add_argument("id", type=str, help="id of the staged video data")
	# `vodbot stage list [id]`
	stager_list = stager_subparser.add_parser("list", epilog=titletext,
		description="lists info on staging area or staged items")
	stager_list.add_argument("id", type=str, help="id of the staged video data")
	
	args = parser.parse_args()

	print(titletext)

	# Initial error checks
	if not exists(args.config):
		util.make_twitch_conf("conf.json")
		util.exit_prog(39,  f'Edit the config file at "{args.config}" before running again.')

	# Handle commands
	if args.cmd == "init":
		init = import_module(".commands.init", "vodbot")
		init.run(args)
	elif args.cmd == "pull":
		pull = import_module(".commands.pull", "vodbot")
		pull.run(args)
	elif args.cmd == "stage":
		stage = import_module(".commands.stage", "vodbot")
		stage.run(args)
	elif args.cmd == "upload":
		upload = import_module(".commands.upload", "vodbot")
		upload.run(args)


if __name__ == "__main__":
	deffered_main()
