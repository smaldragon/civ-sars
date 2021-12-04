import re
import json
import time
from os import environ

re_coord = re.compile("\((.*?)\)")
re_comment = re.compile("#.*")

features = []
dest_stack = []
with open(r'sars_tree.txt') as f:
  cur_ident=0
  for line in f.readlines():
    ident=0
    striped = line.strip()
    name = striped.split(" ")[0]
    # Parse Coordinates
    x,y,z = None,None,None
    coord_parse = re_coord.search(striped)
    if coord_parse is not None:
      coords = coord_parse.group(0)[1:-1].split(",")
      if len(coords) == 2:
        x = int(coords[0])
        z = int(coords[1])
      elif len(coords)==3:
        x = int(coords[0])
        y = int(coords[1])
        z = int(coords[2])
    # Parse comment
    comment = None
    comment_parse = re_comment.search(striped)
    if comment_parse is not None:
      comment = comment_parse.group(0)[1:]
    # Parse /dest
    dest = "/dest $"
    for c in line:
      if c in (" ","\t"):
        ident+=1
      else:
        break
    for i in range(len(dest_stack)-1,-1,-1):
      item = dest_stack[i]
      if ident <= item[1]:
        dest_stack.pop(i)
    dest_stack.append((name,ident))
    for i in dest_stack:
      dest+=f" {i[0]}"
    # Add to ccmap feature list
    if x is not None and z is not None:
      o={'name':name,'x':x,'z':z,'dest':dest,'id':'ccmap:sars/station/'+striped}
      if y is not None:
        o['y'] = y
      if comment is not None:
        o['note'] = comment
      features.append(o)

presentations = [
    {
        "name": "Rails and Stops (SARS)",
        "style_base": {
            "color": "#008844",
        },
        "zoom_styles": {
            "-6": { "name": None },
            "-2": { "name": "$name" },
        },
    },
]
collection = {
    "name": "Rails",
    "info": {
        "version": "3.0.0-beta3",
        "last_update": environ.get('LAST_UPDATE') or int(time.time()),
    },
    "presentations": presentations,
    "features": features,
}

collection_string = json.dumps(collection, indent = None, separators = (',', ':'), sort_keys = True)
# apply line breaks for readability and nice diffs
collection_string = collection_string.replace("},{", "},\n{")
print(collection_string)

with open('ccmap.json','w') as f:
    f.write(collection_string)
