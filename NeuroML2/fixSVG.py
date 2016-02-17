import sys

with open(sys.argv[1], "r") as file:
    svg = file.read()

import re
rx = re.compile(r"<svg(.*?)>")
svg = rx.sub(r'<svg \1 viewBox="0 0 2000 2000">', svg)

with open(sys.argv[1], 'wb') as file:
    file.write(svg)