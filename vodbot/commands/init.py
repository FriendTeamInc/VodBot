# Initialization of VodBot, setting up config, etc.

from os.path import exists

import vodbot.util as util
import vodbot.config as config


def run(args):
	# check if the config exists and ask if it should be overwritten
	if exists(args.output):
		input("It seems a file already exists here. Press enter if you wish to continue, press Ctrl+C to quit.")
		print("Overwriting file...")

	# test write the config.
	try:
		util.make_dir(args.output.parent)
		with open(str(args.output), "w") as f:
			pass
	except FileNotFoundError:
		util.exit_prog(67, f"Cannot create file at `{args.output}`.")
	
	print("Creating default config...")
	
	# create directories now
	util.make_dir(config.DEFAULT_CONFIG.vods)
	util.make_dir(config.DEFAULT_CONFIG.clips)
	util.make_dir(config.DEFAULT_CONFIG.temp)
	util.make_dir(config.DEFAULT_CONFIG.stage)

	# now write the config
	try:
		with open(str(args.output), "w") as f:
			f.write(config.DEFAULT_CONFIG.to_json(indent="\t"))
	except FileNotFoundError:
		util.exit_prog(68, f"Cannot create file at `{args.output}`, despite being able to before.")

	print(f"Finished, the config can be edited at `{args.output}`.")
