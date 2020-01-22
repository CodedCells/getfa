import os, requests, json, time, shutil

''' TODO
Better variable names
Make code prettier
Add auto-config
Add easy secret input
'''

msgs = {
    'log': 'You are not logged in:\n\t1. Find your "a" and "b" cookies on Fur Affinity\n\t2. Create a text file named secret.json\n\t3. Write this in the file, replace insert with the cookie, and save\n\n{\n\t"a": "INSERT A COOKIE",\n\t"b": "INSERT B COOKIE"\n}\n',
    'jsone': 'The file "{}" could not be loaded.\n\n{}\n',
    'newcfg': 'You didn\'t have a config.json, I just made you one.\nPlease set "target" to your user favourites\nConfigure your data and file dirs.\n\tThe first one is where new files will be saved\n\tThe others allow you to prevent files duplication over different instances.'
    }

def read_file(fn, mode='r', encoding='utf-8'):
    # read a file on a single line
    if mode == 'rb':encoding = None# saves writing it a few times
    with open(fn, mode, encoding=encoding) as file:
        data = file.read()
        file.close()
    
    return data


def read_json(fn):
    with open(fn, 'r') as file:
        return json.load(file)

def save_json(fn, d):
    s = json.dumps(d)
    with open(fn, 'w') as file:
        file.write(s)
        file.close()
    return

def get_prop(p, i, t='"', o=1):
    # split string by start and stop
    return i.split(p)[o].split(t)[0]


if os.path.isfile('secret.json'):
    try:cookies = read_json('secret.json')
    except Exception as e:
        input(msgs['jsone'].format('secret.json', e))
        exit()
else:
    input(msgs['log'])
    exit()


if os.path.isfile('config.json'):
    try:cfg = read_json('config.json')
    except Exception as e:
        input(msgs['jsone'].format('config.json', e))
        exit()
else:
    input(msgs['newcfg'])
    # TODO IMPLEMENT BASIC CONFIG
    exit()

session = requests.Session()
session.cookies.update(cookies)


def check_login(d, label):
    if 'The owner of this page' in d:
        print('Not logged in', label)
        input()
        exit()
    elif 'The submission you' in d:
        print('404!', label)
        return False
    
    return True

# Quick login check
x = session.get('http://www.furaffinity.net/view/34445360/')
check_login(x.text, 'Start')
del x


# loading known posts
if os.path.isfile('known.json'):
    with open('known.json', 'r') as fh:
        dj = json.load(fh)

else:
    print('Creating new known.json, this may take a while\n')
    dj = {}


url = cfg['target']
while url != '':
    print(url)
    req = session.get(url)
    d = str(req.content)
    f = get_prop('<section id="gallery-favorites" class="gallery s-250 ">', d, t='</section>')
    f = ['<figure id="' + x.split('-->')[0] for x in f.split('<figure id="')[1:]]
    j = {}
    got = 0
    
    for e in f:
        i = {
            'postid': get_prop('figure id="sid-', e),
            'artist': get_prop(' title="', e, o=3),
            'title': get_prop(' title="', e, o=2),
            'rating': get_prop('r-', e, t=' ')
            }

        if i['postid'] in dj:got += 1
        else:j[i['postid']] = i
    
    dj.update(j)
    
    if 'button standard right" href="' in d:
        nurl = get_prop('button standard right" href="', d)
        if nurl.startswith('/'):nurl = 'http://www.furaffinity.net' + nurl
        if url == nurl:input('HALT: Same URL')
        url = str(nurl)
    else:
        url = ''
    
    if len(f) == got:
        url = ''

    print('SAVING, DO NOT TERMINATE...', end=' ')
    save_json('known.json', dj)
    print('DONE!')

print('Know', len(dj), 'posts')
c = 0
la = 0

data = {
        x: set(y.split('_')[0] for y in os.listdir(x)) for x in cfg['dataDirs']
    }
file = {
        x: set(y.split('.')[0] for y in os.listdir(x)) for x in cfg['fileDirs']
    }
file_all = []
for f in cfg['fileDirs']:
    file_all += file[f]

file_all = set(file_all)

if os.path.isfile('posts404.json'):fnf = read_json('posts404.json')
else:fnf = []
sa = 0

def get_ext(data):
    e = 'txt'
    if data.startswith(b'GIF8'):e = 'gif'
    elif data.startswith(b'\x89PNG'):e = 'png'
    elif data.startswith(b'\xff\xd8'):e = 'jpg'
    elif data.startswith(b'CWS') or data.startswith(b'FWS'):e = 'swf'
    elif data.startswith(b'%PDF'):e = 'pdf'
    return e

for post in reversed(list(dj.keys())):
    c += 1
    
    igot =  post in file_all
    if igot and post in data[cfg['dataDirs'][0]]:continue
    if post in fnf:continue
    
    gotd = False
    for di in cfg['dataDirs']:
        if post in data[di]:
            gotd = True
            if di != cfg['dataDirs'][0]:shutil.copyfile('{}{}_desc.html'.format(di, post), '{}{}_desc.html'.format(cfg['dataDirs'][0], post))
            with open('{}{}_desc.html'.format(di, post), 'r', encoding='utf8') as fh:
                d = fh.read()
            
            if not check_login(d, 'STORED: ' + post):continue# STORED 404
    
    if not gotd:
        print('GET DATA', post)
        sg = session.get('http://www.furaffinity.net/view/{}/'.format(post))
        if check_login(sg.text, json.dumps(dj[post])):
            with open('{}{}_desc.html'.format(cfg['dataDirs'][0], post), 'wb') as fh:
                fh.write(sg.content)
        else:
            fnf.append(post)
            sa += 1
            continue
        
        time.sleep(.1)
        
        d = sg.text
    
    if igot:continue
    
    if 'class="download"><a href="' in d:
        fp = get_prop('class="download"><a href="', d)
    elif 'data-fullview-src="' in d:
        fp = get_prop('data-fullview-src="', d)
    else:
        print('Unknown Image', post, dj[post])
        continue
    
    print('GET IMG ', post)
    sg = session.get('http:' + fp)
    fn = cfg['fileDirs'][0] + post + '.' + get_ext(sg.content)
    
    with open(fn, 'wb') as fh:
        fh.write(sg.content)
    
    time.sleep(.1)
    
    if c//500 > la:
        print('\t', (c//500)*500)
        if sa > 0:save_json('posts404.json', fnf)
        sa = 0
        la = c//500

if sa > 0:save_json('posts404.json', fnf)
if not cfg['exitOnComplete']:input('Complete!')
