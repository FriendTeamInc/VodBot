from sys import argv as sys_argv

# Taken from https://github.com/tartley/colorama#recognised-ansi-sequences
COLOR_CODES = {
	"r": "\033[0m", # reset
	"l": "\033[1m", # light
	"d": "\033[2m", # dim

	"fK": "\033[30m",
	"fR": "\033[31m",
	"fG": "\033[32m",
	"fY": "\033[33m",
	"fB": "\033[34m",
	"fM": "\033[35m",
	"fC": "\033[36m",
	"fW": "\033[37m",

	"bK": "\033[40m",
	"bR": "\033[41m",
	"bG": "\033[42m",
	"bY": "\033[43m",
	"bB": "\033[44m",
	"bM": "\033[45m",
	"bC": "\033[46m",
	"bW": "\033[47m"
}

USE_COLOR = "--no-color" not in sys_argv

def colorize(text: str):
	for k, v in COLOR_CODES.items():
		text = text.replace("#" + k, v)
	return text

def strip_color(text: str):
	for k in COLOR_CODES:
		text = text.replace("#" + k, "")
	return text

def cprint(*args, **kwargs):
	args = [colorize(txt) if USE_COLOR else strip_color(txt) for txt in args]
	print(*args, **kwargs)