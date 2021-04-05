# Upload, command to upload staged videos to YouTube
# References:
# https://developers.google.com/youtube/v3/guides/uploading_a_video
# https://learndataanalysis.org/how-to-upload-a-video-to-youtube-using-youtube-data-api-in-python/

from .stage import StageData

import vodbot.util as util
import pickle
import json
from datetime import datetime
from os import listdir as os_listdir
from os.path import exists as os_exists, isfile as os_isfile
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from google.auth.transport.requests import Request


# Default path
vodbotdir = util.vodbotdir

CLIENT_SECRET_FILE = vodbotdir / 'youtube-conf.json'
API_NAME = "youtube"
API_VERSION = "v3"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def load_stage(stage_id):
	jsonread = None
	try:
		with open(str(vodbotdir / "stage" / (stage_id+".stage"))) as f:
			jsonread = json.load(f)
	except FileNotFoundError:
		util.exit_prog(46, f'Could not find stage "{stage_id}". (FileNotFound)')
	except KeyError:
		util.exit_prog(46, f'Could not parse stage "{stage_id}" as JSON. Is this file corrupted?')
	
	_title = jsonread['title']
	_desc = jsonread['desc']
	_ss = jsonread['ss']
	_to = jsonread['to']
	_streamers = jsonread['streamers']
	_datestring = jsonread['datestring']
	_filename = jsonread['filename']

	return StageData(_title, _desc, _ss, _to, _streamers, _datestring, _filename)


EPOCH = datetime.utcfromtimestamp(0)
def sort_stagedata(stagedata):
	date = datetime.strptime(stagedata["datestring"], "%Y/%m/%d")
	return (date - EPOCH).total_seconds()


def upload_video(service, stagedata):
	# send request to youtube to upload
	request_body = {
		"snippet": {
			"categoryId": 20
		}
	}

	# create media file
	media_file = MediaFileUpload()

	# create upload request and execute
	response_upload = service.videos().insert(
		part="snippet,status",
		body=request_body,
		media_body=media_file
	).execute()


def run(args):
	# authenticate youtube service
	if not os_exists(str(vodbotdir / "youtube-conf.json")):
		util.exit_prog(19, "Missing `youtube-conf.json`.")

	service = None
	credentials = None
	pickle_filename = f"tkn_{API_NAME}_{API_VERSION}.pkl"

	if os_exists(str(vodbotdir / pickle_filename)):
		with open(str(vodbotdir / pickle_filename), "rb") as f:
			credentials = pickle.load(f)
	
	if not credentials or not credentials.valid:
		if credentials and credentials.expired and credentials.refresh_token:
			credentials.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET_FILE), SCOPES)
			credentials = flow.run_local_server()
		
		with open(str(vodbotdir / pickle_filename), "wb") as f:
			pickle.dump(credentials, f)
	
	try:
		service = build(API_NAME, API_VERSION)
	except Exception as err:
		util.exit_prog(50, f"Failed to connect to YouTube API, \"{err}\"")
	
	# Handle id/all
	if args.id == "all":
		# create a list of all the hashes and sort by date streamed, upload chronologically
		stages = [d[:-6] for d in os_listdir(str(vodbotdir / "stage"))
			if os_isfile(str(vodbotdir / "stage" / d)) and d[-5:] == "stage"]
		
		stagedatas = [load_stage(stage) for stage in stages]
		
		stagedatas.sort(key=sort_stagedata)

		print(stagedatas)
	else:
		# check if stage exists, and prep it for upload
		if os_exists(str(vodbotdir / "stage" / (args.id+".stage"))):
			upload_video(service, args.id)
		else:
			util.exit_prog(51, f"Could not find stage {args.id}.")
