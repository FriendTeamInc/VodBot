# Upload, command to upload staged videos to YouTube
# References:
# https://developers.google.com/youtube/v3/guides/uploading_a_video
# https://learndataanalysis.org/how-to-upload-a-video-to-youtube-using-youtube-data-api-in-python/

from .stage import StageData

import vodbot.util as util
from vodbot.printer import cprint, colorize

import pickle
import json
from datetime import datetime
from os import listdir as os_listdir, environ as os_environ, remove as os_remove
from os.path import exists as os_exists, isfile as os_isfile

from httplib2.error import HttpLib2Error, HttpLib2ErrorWithResponse

from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError, ResumableUploadError
from google.auth.transport.requests import Request


# Default path
vodbotdir = util.vodbotdir

CLIENT_SECRET_FILE = vodbotdir / 'youtube-conf.json'
API_NAME = "youtube"
API_VERSION = "v3"
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

RETRIABLE_EXCEPTS = (HttpLib2Error, HttpLib2ErrorWithResponse, IOError)


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
	date = datetime.strptime(stagedata.datestring, "%Y/%m/%d")
	return (date - EPOCH).total_seconds()


def upload_video(service, stagedata):
	# send request to youtube to upload
	request_body = {
		"snippet": {
			"categoryId": 20,
			"title": stagedata.title,
			"description": stagedata.desc
		},
		"status": {
			"privacyStatus": "private",
			"selfDeclaredMadeForKids": False
		}
	}

	# create media file
	media_file = MediaFileUpload(stagedata.filename, chunksize=-1, resumable=True)

	# create upload request and execute
	response_upload = service.videos().insert(
		part="snippet,status",
		body=request_body,
		media_body=media_file
	)

	resp = None
	retry = 0
	while resp is None:
		try:
			print(f"Uploading stage {stagedata.hashdigest}")
			status, resp = response_upload.next_chunk()
			if resp is not None:
				if "id" in resp:
					print(f"Video (ID:{resp['id']}) was uploaded.")
				else:
					util.exit_prog(99, f"Unexpected upload failure occurred, \"{resp}\"")
		except ResumableUploadError as err:
			if err.resp.status == 403:
				util.exit_prog(403, "API Quota exceeded, you'll have to wait ~24 hours to upload.")
		except HttpError as err:
			if err.resp.status in [500, 502, 503, 504]:
				print(f"An HTTP error has occured, retrying ({err.resp.status},{err.content})")
			else:
				raise
		except RETRIABLE_EXCEPTS as err:
			print(f"An HTTP error has occured, retrying ({err})")


def run(args):
	# handle logout
	if args.id == "logout":
		try:
			os_remove(str(vodbotdir / pickle_filename))
		except:
			util.exit_prog(11, "Failed to remove credentials for YouTube account.")
		
		return
	
	# load stages, but dont upload
	# Handle id/all
	stagedata = None
	stagedatas = None
	if args.id == "all":
		cprint("#dLoading stages...", end=" ")
		# create a list of all the hashes and sort by date streamed, upload chronologically
		stages = [d[:-6] for d in os_listdir(str(vodbotdir / "stage"))
			if os_isfile(str(vodbotdir / "stage" / d)) and d[-5:] == "stage"]
		stagedatas = [load_stage(stage) for stage in stages]
		stagedatas.sort(key=sort_stagedata)
	else:
		cprint("#dLoading stage...", end=" ")
		# check if stage exists, and prep it for upload
		stagedata = load_stage(args.id)
		cprint(f"About to upload stage {stagedata.hashdigest}.#r")

	# authenticate youtube service
	if not os_exists(str(vodbotdir / "youtube-conf.json")):
		util.exit_prog(19, "Missing `youtube-conf.json`.")

	cprint("Authenticating with Google...", end=" ")

	# temporary work around until something more substantial can be figured out.
	# TODO: make this not garbage
	os_environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(vodbotdir / "vodbot-credentials.json")

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
	
	cprint("Authenticated.", end=" ")
	
	# Handle id/all
	if args.id == "all":
		# begin to upload
		cprint(f"About to upload {len(stagedatas)} stages.#r")
		for stage in stagedatas:
			upload_video(service, stage)
	else:
		# upload stage
		cprint(f"About to upload stage {stagedata.hashdigest}.#r")
		upload_video(service, stagedata)
	
