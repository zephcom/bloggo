#!/usr/bin/python

import io, sys, json, argparse
from jinja2 import Template

def buildArticle(filename, data, old, new):
    with open('templates/post.html', 'r') as f:
        t = Template(f.read())
    page = t.render(data, old_title=old['title'],
                          new_title=new['title'],
                          old_filename=old['filename'],
                          new_filename=new['filename'])
    with open('build/' + filename + '.html', 'w') as o:
        o.write(page)


def buildArchive(filename, data):
    with open('templates/archive.html', 'r') as f:
        t = Template(f.read())
    page = t.render(data)
    with open('build/' + filename + '.html', 'w') as o:
        o.write(page)


def buildTagpage(tag, data):
    with open('templates/tag.html', 'r') as f:
        t = Template(f.read())
    page = t.render(data, tag=tag)
    with open('build/tag-' + tag + '.html', 'w') as o:
        o.write(page)


def buildTagindex(tag_list, data):
    tlist = {}
    for tag in set(tag_list):
        tlist[tag] = tag_list.count(tag)
    with open('templates/tag_index.html', 'r') as f:
        t = Template(f.read())
    page = t.render(data, tagset = set(tag_list),
                          tlist = tlist)
    with open('build/tags.html', 'w') as o:
        o.write(page)


def fetchMetadata(filename):
    with open(filename, 'r') as f:
        return json.loads(f.read())


def updateMetadata(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, sort_keys = True, indent = 4)


def generatePost():
    return {'date': input('Date: '),
            'title': input('Title: '),
            'article': input('Text: '),
            'tags': input('Tags: ').split(','),
            'filename': input('Filename: '),
            'current': 'true'}


def listPosts(postlist):
    print('Date: \t Filename:')
    for n in postlist:
        print(n['date'] + '\t' + n['filename'])


def destroyPost(postlist, filename):
    """Destroys the specified post and returns an updated list."""
    i = 0
    for n in postlist:
        if n['filename'] == filename:
            print(n['filename'])
            print('MATCHED\tpost#=' + str(i))
            del postlist[i]
            postlist[-1]['current'] = "true"
        i = i + 1
    return postlist


parser = argparse.ArgumentParser()
parser.add_argument('-n', '--new',
                    help='Generate a new entry in the metadata.json file',
                    action='store_true',)
parser.add_argument('-d', '--delete',
                    help='Delete entry specified by filename',
                    action='store_true')
parser.add_argument('-l', '--list',
                    help='List all entries stored in metadata.json file',
                    action='store_true')
args = parser.parse_args()

# Import(ant) metadata heh
content = {'post': fetchMetadata('metadata.json')}
# Create a set of tags to be populated later
tag_list = []

if args.new:
    for n in content['post']:
        n['current'] = 'false'
    content['post'].append(generatePost())
    updateMetadata('metadata.json', content['post'])
if args.list:
    listPosts(content['post'])
    sys.exit()
if args.delete:
    listPosts(content['post'])
    destroyPost(content['post'], input('Filename: '))
    updateMetadata('metadata.json', content['post'])


## MAIN
## Identify current page
for n in content['post']:
    if n['current'].lower() == "true":
        current_post = n['filename']

## Build all article pages
i = 0;
for n in content['post']:
    ## Doing something with older/newer, should get the title and filename to older/newer posts and send
    ## to the buildArticle function, this is the worst code!
    if i == 0:
        old = {'title': '', 'filename': ''}
    else:
        old = {'title': content['post'][i - 1]['title'],
               'filename': content['post'][i - 1]['filename']}
    if i == len(content['post']) - 1:
        new = {'title': '', 'filename': ''}
    else:
        new = {'title': content['post'][i + 1]['title'],
                'filename': content['post'][i + 1]['filename']}
    buildArticle(n['filename'], n, old, new)
    if n['current'].lower() == "true":
        buildArticle('index', n, old, new)
    for tag in n['tags']:
        tag_list.append(tag)
    i = i + 1

## Create individual tag pages
print('Tags: ')
for tag in set(tag_list):
    print(tag)
    buildTagpage(tag, content)

## Create index of tags
buildTagindex(tag_list, content)

## Build navigation page
buildArchive('archive', content)

