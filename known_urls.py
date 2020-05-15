# dump known.json post ids as full urls

import json

with open('known.json', 'r') as fh:
    known = json.load(fh)
    fh.close()

with open('known_urls.txt', 'w') as fh:
    fh.write('// {} urls'.format(len(known)))
    for postid in known:
        fh.write('\nhttps://www.furaffinity.net/view/{}/'.format(postid))
    fh.close()
