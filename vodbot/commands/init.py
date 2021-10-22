# Initialization of VodBot, setting up config, etc.

import json
import re
from os.path import isabs, exists

import vodbot.util as util
from vodbot.printer import cprint

vodbotdir = util.vodbotdir
DEFAULT_CONF = util.DEFAULT_CONF
DEFAULT_CONF_PATH = util.DEFAULT_CONF_PATH


def create_config(args):
	channels = []
	timezone = "" # switch to UTC only
	
	# these are for determining directories.
	# we need to make sure any that are already provided are absolute right now.
	# we do it now so that the user doesn't enter in anything before receiving
	# an error that boots them out of the program.
	parts = [
		[args.voddir, "VODs", DEFAULT_CONF['vod_dir']],
		[args.clipdir, "Clips", DEFAULT_CONF['clip_dir']],
		[args.tempdir, "temporary data", DEFAULT_CONF['temp_dir']],
		[args.stagedir, "staged data", DEFAULT_CONF['stage_dir']]
	]

	for part in parts:
		if part[0]:
			if not isabs(part[0]):
				util.exit_prog(150, f"Path `{part[0]}` for {part[1]} is not an absolute path.")
			part.append(part[0])

	# Ask for channels
	if not args.channels:
		cprint("Enter the login names of the Twitch channels you'd like to have archived.")
		cprint("When you're done, just leave the input empty and press enter.")
		cprint("Example: the url is `https://twitch.tv/notquiteapex`, enter `notquiteapex`")
		while True:
			channel = input("> ")
			if channel == "" and len(channels) > 0:
				break
			elif channel == "" and len(channels) == 0:
				cprint("#fRError#r, no channels given.")
			elif not re.match(r"^[a-zA-Z0-9][\w]{0,24}$", channel): # https://discuss.dev.twitch.tv/t/3855/4
				cprint("#fRError#r, channel names only contain characters A-Z, 0-9, and '_'. They also can't start with '_'.")
			else:
				channels += [channel]
	else:
		channels = args.channels

	# Ask for timezone as UTC string
	# We only absolutely need the hours and minutes offset, and we regex it out of the string.
	if not args.timezone:
		cprint("Enter the UTC timezone for timedate referencing. Only use +, -, and numbers.")
		cprint("#dExample: `+0000` for UTC, `-0500` for America's EST. Default: `+0000`#r")
		while True:
			tz = input("> ")
			if tz == "":
				tz = "+0000"
				break
			elif not re.match(r"^[+-]\d\d\d\d$", tz):
				cprint("Error, UTC string not recognized.")
			else:
				break
	else:
		timezone = args.timezone
		# check that entered timezone is valid

	# ask for directories (any provided by the terminal arguments are already handeled.)
	cprint("Now let's get some directories to store data. The entered paths must be absolute, not relative.")
	cprint("If you'd like to use the default location listed, just leave the input blank and press enter.")

	for part in parts:
		if not part[0]:
			cprint(f"Enter where {part[1]} should be stored.\n#dDefault: `#l{part[2]}`#r")
			while True:
				inpdir = input("> ")
				if inpdir == "":
					part.append(part[2])
					break
				elif isabs(inpdir):
					# TODO: check if directory can be created? a file might already exist?
					part.append(inpdir)
					break
				else:
					cprint(f"#fRError#r, directory `#l{inpdir}#r` is not an absolute path for a directory.")

	# ready to write it all, go!
	cprint("#dWriting config...#r")
	# Edit default config variable.
	DEFAULT_CONF['twitch_channels'] = channels
	DEFAULT_CONF['stage_timezone'] = timezone
	DEFAULT_CONF['vod_dir'] = parts[0][3]
	DEFAULT_CONF['clip_dir'] = parts[1][3]
	DEFAULT_CONF['temp_dir'] = parts[2][3]
	DEFAULT_CONF['stage_dir'] = parts[3][3]
	# the file gets written outside this function


def run(args):
	# check if the config exists and ask if it should be overwritten
	if exists(args.output):
		input("It seems a file already exists here. Press enter if you wish to continue, otherwise press Ctrl+C to quit.")
		input("This operation will overwrite this file. Do you have a backup? Press enter again to continue, otherwise press Ctrl+C to quit.")
		input("Last time, are you absolutely certain you want to overwrite this file? Press enter again to continue, otherwise press Ctrl+C to quit.")
		print("Overwriting file...")

	# test write the config.
	try:
		util.make_dir(args.output.parent)
		with open(str(args.output), "w") as f:
			pass
	except FileNotFoundError:
		util.exit_prog(67, f"Cannot create file at \"{args.output}\".")
	
	# see which config we should make
	if args.default:
		# generate default config
		cprint("#dCreating default config...#r")
	else:
		# generate config from inputs
		create_config(args)
	
	# create directories now
	util.make_dir(DEFAULT_CONF['vod_dir'])
	util.make_dir(DEFAULT_CONF['clip_dir'])
	util.make_dir(DEFAULT_CONF['temp_dir'])
	util.make_dir(DEFAULT_CONF['stage_dir'])

	# now write the config
	try:
		#util.make_dir(args.output.parent) # redundant
		with open(str(args.output), "w") as f:
			json.dump(DEFAULT_CONF, f, indent=4)
	except FileNotFoundError:
		util.exit_prog(68, f"Cannot create file at \"{args.output}\" despite being able to before.")

	# list the location of the config and say what can be edited outside this command
	cprint(f"#fGFinished#r, the config can be edited at `#l{str(vodbotdir / 'conf.json')}#r`.")
