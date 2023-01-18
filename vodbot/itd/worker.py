# Based on https://github.com/ihabunek/twitch-dl/blob/master/twitchdl/download.py
# Modified to fit the project a bit better, originally licensed under GPLv3.
# Modifications include shortening some functions, removing redundant bits,
# and changing certain printouts to be more colorful.

from vodbot.printer import cprint
from vodbot.util import format_duration, format_size

import os
import requests

from datetime import datetime
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, as_completed, wait
from functools import partial
from requests.exceptions import RequestException


CHUNK_SIZE = 1024
CONNECT_TIMEOUT = 5
RETRY_COUNT = 5


class DownloadFailed(Exception):
	pass

class DownloadCancelled(Exception):
	pass


def _download(url, path):
	tmp_path = path + ".tmp"
	response = requests.get(url, stream=True, timeout=CONNECT_TIMEOUT)
	size = 0
	with open(tmp_path, 'wb') as target:
		for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
			target.write(chunk)
			size += len(chunk)

	os.rename(tmp_path, path)
	return size


def download_file(url, path, retries=RETRY_COUNT):
	if os.path.exists(path):
		return os.path.getsize(path), True

	for _ in range(retries):
		try:
			return _download(url, path), False
		except RequestException:
			pass

	raise DownloadFailed("sadge")


def _print_progress(video_id, futures):
	downloaded_count = 0
	downloaded_size = 0
	existing_size = 0
	max_msg_size = 0
	start_time = datetime.now()
	total_count = len(futures)

	try:
		for future in as_completed(futures):
			(size, existed) = future.result()
			downloaded_count += 1
			downloaded_size += size
			if existed:
				existing_size += size

			percentage = 100 * downloaded_count // total_count
			est_total_size = int(total_count * downloaded_size / downloaded_count)
			duration = (datetime.now() - start_time).seconds
			speed = (downloaded_size - existing_size) // duration if duration else 0
			remaining = (total_count - downloaded_count) * duration / downloaded_count

			msg = " ".join([
				f"#fM#lVOD#r `#fM{video_id}#r` pt#fC{downloaded_count}#r/#fB#l{total_count}#r,",
				f"#fC{format_size(downloaded_size)}#r/#fB#l~{format_size(est_total_size)}#r #d({percentage}%)#r;",
				f"at #fY~{format_size(speed)}/s#r;" if speed > 0 else "",
				f"#fG~{format_duration(remaining)}#r left" if speed > 0 else "",
			])

			max_msg_size = max(len(msg), max_msg_size)
			cprint("#c\r" + msg.ljust(max_msg_size), end="")
	except KeyboardInterrupt:
		done, not_done = wait(futures, timeout=0)
		for future in not_done:
			future.cancel()
		wait(not_done, timeout=None)
		raise DownloadCancelled()


def download_files(video_id, base_url, target_dir, vod_paths, max_workers):
	urls = [base_url + path for path in vod_paths]
	targets = [str(target_dir / path) for path in vod_paths]
	partials = (partial(download_file, url, path) for url, path in zip(urls, targets))

	with ThreadPoolExecutor(max_workers=max_workers) as executor:
		futures = [executor.submit(fn) for fn in partials]
		_print_progress(video_id, futures)

	return OrderedDict(zip(vod_paths, targets))
