ROSTER_LOCATION = '/afs/sipb/admin/text/members/members_and_prospectives'

sipb_roster = {}
with open(ROSTER_LOCATION) as f:
    for line in f:
        if line.startswith('#'):
            continue

        contents = line.split()
        if len(contents) >= 2:
            sipb_roster[contents[0]] = contents[1]
