import requests

ROSTER_LOCATION = (
    "https://stuff.mit.edu/afs/sipb/admin/text/members/members_and_prospectives"
)

sipb_roster = {}
req = requests.get(ROSTER_LOCATION)
for line in req.text.split("\n"):
    if line.startswith("#"):
        continue

    contents = line.split()
    if len(contents) >= 2:
        sipb_roster[contents[0]] = contents[1]
