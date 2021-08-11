# Initialization of VodBot, setting up config, etc.

import json
import re
from os.path import isabs

import vodbot.util as util
import vodbot.printer as cp

vodbotdir = util.vodbotdir
DEFAULT_CONF = util.DEFAULT_CONF


def create_config(args):
	channels = []
	timezone = "" # switch to UTC only

	# Ask for channels
	if not args.channels:
		cp.cprint("Enter the login names of the Twitch channels you'd like to have archived.")
		cp.cprint("When you're done, just leave the input empty and press enter.")
		cp.cprint("Example: the url is `https://twitch.tv/notquiteapex`, enter `notquiteapex`")
		while True:
			channel = input("> ")
			if channel == "":
				break
			elif channel.isalnum():
				cp.cprint("Error, channel names must be alphanumeric.")
			else:
				channels += [channel]
	else:
		channels = args.channels

	# Ask for timezone as UTC string
	if not args.timezone:
		cp.cprint("Enter the UTC timezone for timedate referencing. Only use +, -, and numbers.")
		cp.cprint("Example: `+0000` for UTC, `-0500` for America's EST. Default: `+0000`")
		regex = re.compile(r"^[+-]\d\d\d\d$")
		while True:
			tz = input("> ")
			if tz == "":
				tz = "+0000"
				break
			elif not regex.match(tz):
				cp.cprint("Error, UTC string not recognized.")
			else:
				break
	else:
		timezone = args.timezone
		# check that entered timezone is valid

	# ask for directories (have defaults ready)
	cp.cprint("Now let's get some directories to store data. The entered paths must be absolute, not relative.")
	cp.cprint("If you'd like to use the default location listed, just leave the input blank and press enter.")

	parts = (
		[args.voddir, "VODs", DEFAULT_CONF['vod_dir']]
		[args.clipdir, "Clips", DEFAULT_CONF['clip_dir']]
		[args.tempdir, "temporary data", DEFAULT_CONF['temp_dir']]
		[args.stagedir, "staged data", DEFAULT_CONF['stage_dir']]
	)

	for part in parts:
		if not part[0]:
			cp.cprint(f"Enter where {part[1]} should be stored.\nDefault: `{part[2]}`")
			inpdir = input("> ")
			if inpdir == "":
				part[3] = inpdir
				break
		else:
			part[3] = part[0]

	# ready to write it all, go!
	cp.cprint("Writing config...")
	# Edit default config variable and write that to file.
	DEFAULT_CONF['twitch_channels'] = channels
	DEFAULT_CONF['stage_timezone'] = timezone
	DEFAULT_CONF['vod_dir'] = parts[0][3]
	DEFAULT_CONF['clip_dir'] = parts[1][3]
	DEFAULT_CONF['temp_dir'] = parts[2][3]
	DEFAULT_CONF['stage_dir'] = parts[3][3]

	with open(str(vodbotdir / "conf.json")) as f:
		json.dump(DEFAULT_CONF, f, indent=4)


def run(args):
	if args.default:
		# generate default config
		cp.cprint("Creating default config...")

		with open(str(vodbotdir / "conf.json")) as f:
			json.dump(DEFAULT_CONF, f, indent=4)
	else:
		# generate config from inputs
		create_config(args)

	# list the location of the config and say what can be edited outside this command
	cp.cprint(f"Finished, the config can be edited at `{str(vodbotdir / 'conf.json')}`.")
