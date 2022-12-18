# based off picauto
# https://gist.github.com/NotQuiteApex/77cdc6c670ec63aff84dd87d672861e5

import subprocess
from os import walk


class PosInf:
    def __init__(self, x,y, s=1):
        self.x = x
        self.y = y
        self.s = s
    
    def __repr__(self):
        return f"PosInf(x={self.x} y={self.y} s={self.s})"
    
    def __str__(self):
        return f"PosInf(x={self.x} y={self.y} s={self.s})"

class HeadInf:
    def __init__(self, name, ox,oy):
        self.name = name
        self.ox = ox
        self.oy = oy
        self.filename = f"heads/{name}.png"
    
    def __repr__(self):
        return f"HeadInf(name={self.name} ox={self.ox} oy={self.oy})"
    
    def __str__(self):
        return f"{self.name}"

class PosHead:
    def __init__(self, pos, head=None):
        self.pos = pos
        self.head = head
    
    def __repr__(self):
        return f"({self.pos},{self.head})"


# take in a StageData, process the data given the config, spit out the path to the image
def generate_thumbnail():

    # to get single frame from a video
    # "ffmpeg" "-ss" "<timestamp>" "-i" "<inputvod.mkv>" "-frames:v" "1" "<tmp/screenshot_output.png>"

    # to generate a thumbnail with imagemagick
    # notes: tx and ty are generated with pos-(offset*scale), s is scale
    # initial: "magick" "-size" "<canvas_width>x<canvas_height>" "canvas:none" "-font" "<text_font>" "-pointsize" "<text_size>"
    # screenshot: "-draw" "image src-over <screenshot_x>,<screenshot_y> <canvas_width>,<canvas_height> \\'<tmp/screenshot_output.png>\\'"
    # cover image: "-draw" "image src-over <cover_x>,<cover_y> <canvas_width>,<canvas_height> \\'<thumbnail/cover.png>\\'"
    # loop over positions and heads: "-draw" "translate <tx>,<ty> scale <s>,<s> image src-over 0,0 0,0 \\'<thumbnail/heads/head.png>\\'"
    # game image: "-draw" "translate <tx>,<ty> scale <s>,<s> image src-over 0,0 0,0 \\'<thumbnail/games/game.png>\\'"
    # text: "-fill" "white" "-stroke" "black" "-strokewidth" "32" "-draw" "gravity NorthWest text <text_x>,<text_y> \\'<textTEXT>\\'"
    # text: "-fill" "white" "-stroke" "white" "-strokewidth" "08" "-draw" "gravity NorthWest text <text_x>,<text_y> \\'<textTEXT>\\'"
    # output: "<tmp/out.png>"

    pass
