# Based on https://github.com/ihabunek/twitch-dl/blob/master/twitchdl/download.py
# Modified to fit the project a bit better, licensed under GPLv3.

import os
import requests

from datetime import datetime
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import partial
from requests.exceptions import RequestException


CHUNK_SIZE = 1024
CONNECT_TIMEOUT = 5
RETRY_COUNT = 5


class DownloadFailed(Exception):
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


def _download_file(url, path, retries=RETRY_COUNT):
	if os.path.exists(path):
		return os.path.getsize(path)

	for _ in range(retries):
		try:
			return _download(url, path)
		except RequestException:
			pass

	raise DownloadFailed("sadge")

def format_duration(total_seconds):
	total_seconds = int(total_seconds)
	hours = total_seconds // 3600
	remainder = total_seconds % 3600
	minutes = remainder // 60
	seconds = total_seconds % 60

	if hours:
		return f"{hours} h {minutes} min"
	elif minutes:
		return f"{minutes} min {seconds} sec"
	else:
		return f"{seconds} sec"

def format_size(bytes_, digits=1):
	units = ["B", "kB", "MB"]
	for x in range(3):
		if bytes_ < 1024:
			if digits > 0:
				return "{{:.{}f}}{}".format(digits, units[x]).format(bytes_)
			else:
				return "{{:d}}{}".format(units[x]).format(bytes_)
		bytes_ /= 1024

	if digits > 0:
		return "{{:.{}f}}{}".format(digits, "GB").format(bytes_)
	else:
		return "{{:d}}{}".format("GB").format(bytes_)

def _print_progress(futures):
	downloaded_count = 0
	downloaded_size = 0
	max_msg_size = 0
	start_time = datetime.now()
	total_count = len(futures)

	for future in as_completed(futures):
		size = future.result()
		downloaded_count += 1
		downloaded_size += size

		percentage = 100 * downloaded_count // total_count
		est_total_size = int(total_count * downloaded_size / downloaded_count)
		duration = (datetime.now() - start_time).seconds
		speed = downloaded_size // duration if duration else 0
		remaining = (total_count - downloaded_count) * duration / downloaded_count

		msg = " ".join([
			f"Downloaded VOD part {downloaded_count}/{total_count}",
			f"({percentage}%){format_size(downloaded_size)}",
			f"of ~{format_size(est_total_size)};",
			f"at {format_size(speed)}/s;" if speed > 0 else "",
			f"remaining ~{format_duration(remaining)}" if speed > 0 else "",
		])

		max_msg_size = max(len(msg), max_msg_size)
		print("\r" + msg.ljust(max_msg_size), end="")


def download_files(base_url, target_dir, vod_paths, max_workers):
	urls = [base_url + path for path in vod_paths]
	targets = [str(target_dir / "{:06d}.ts".format(k)) for k, _ in enumerate(vod_paths)]
	partials = (partial(_download_file, url, path) for url, path in zip(urls, targets))

	with ThreadPoolExecutor(max_workers=max_workers) as executor:
		futures = [executor.submit(fn) for fn in partials]
		_print_progress(futures)

	return OrderedDict(zip(vod_paths, targets))
