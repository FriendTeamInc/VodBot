import os
import sys
import toml
from pathlib import Path

defaultclientid = "TWITCH.CLIENT-ID"
defaultclientsecret = "TWITCH.CLIENT-SECRET"

def make_dir(directory):
	os.mkdir(str(directory))

def make_conf(directory):
	basetoml = {
		"twitch": {
			"client-id":defaultclientid,
			"client-secret":defaultclientsecret,
			"channels":["notquiteapex","juicibox","batkigu"]
		}
	}

	filedata = toml.dumps(basetoml)

	with open(str(directory / "conf.toml"), "w") as f:
		f.write(filedata)

def exit_prog(code=0, errmsg=None):
	if code != 0:
		msg = f"ERROR! ({code}) "
		if errmsg != None:
			msg += errmsg
		print(msg)

	print("Exiting...")
	sys.exit(code)