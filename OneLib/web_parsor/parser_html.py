import urllib.request
import re
try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup
    import bs4
with open('./a.html', 'r') as f:
    parsed_html = BeautifulSoup(f.read())
items = parsed_html.body.find('table', attrs={'class':'table table-bordered table-striped'})

def ParseTD(td):
    return td.contents[0].strip()

def RemoveIndex(s):
    return re.sub(r'\(\d/\d\)', '', s)

def ParseTitle(week):
    week_id = ParseTD(week.find_all('td')[0])
    week_title = RemoveIndex(ParseTD(week.find_all('td')[1]))
    print(week_id, '--', week_title)
    file_name = '%s_%s' %(week_id, week_title)
    file_name.strip()
    return file_name +'.mp4'

def ParseVideoURL(week):
    for a in week.find_all('a'):
        if a.get('href') and '.mp4' in a.get('href'):
            video_url = a.get('href')
            print(video_url)
            return video_url
    else:
        print('video not founded:\n', week)
        return None



for week in items.tbody.contents:
    if type(week) != bs4.element.Tag:
        continue
    if not week.find('a'):
        continue
    try:
        title = ParseTitle(week)
        url = ParseVideoURL(week)
        if url:
            print('Download %s --> %s' % (url, title))
            urllib.request.urlretrieve(url, title)
    except Exception as e:
        print('Error:------------\n', week)
        print(e)
        print('===========')
        raise(e)
