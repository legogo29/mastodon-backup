#!/usr/bin/env python3
# Copyright (C) 2017  Alex Schroeder <alex@gnu.org>
# Copyright (C) 2017  Steve Ivy <steveivy@gmail.com>

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.

import sys
import os.path
from html import escape
import html2text
import datetime
import dateutil.parser
from urllib.parse import urlparse
from . import core

header_template = '''\
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<title>%s</title>
<style type="text/css">
body {
        font-family: sans-serif;
        background: #191b22;
        font-size: 14px;
        line-height: 18px;
        font-weight: 400;
        color: #fff;
        text-rendering: optimizelegibility;
        -webkit-font-feature-settings: "kern";
        font-feature-settings: "kern";
        -webkit-text-size-adjust: none;
        -moz-text-size-adjust: none;
        -ms-text-size-adjust: none;
        text-size-adjust: none;
        -webkit-tap-highlight-color: transparent;
}
.column {
        background: #282c37;
        padding: 10px;
        margin: auto;
        max-width: 80ex;
}
h1 {
        color: #fff;
        font-size: 20px;
        line-height: 27px;
        font-weight: 500;
        overflow: hidden;
        text-overflow: ellipsis;
        text-align: center;
}
.account {
        text-align: center;
}
.account .nick {
        color: #2b90d9;
        margin-bottom: 10px;
}
.account .bio, .bio a, .bio a:visited {
        color: #d9e1e8;
}
.meta {
        color: #606984;
        font-size: 15px;
}
.meta strong {
        font-weight: 500;
}
a {
        text-decoration: none;
}
a:hover {
        text-decoration: underline;
}
.wrapper {
        padding-top: 10px;
        border-top: 1px solid #393f4f;
        position: relative;
        min-height: 59px;
}
.status {
        padding-left: 78px;
}
.boosted a {
        color: #606984;
}
.boosted a:visited {
        color: #606984;
}
.boosted {
        padding-bottom: 10px;
        padding-left: 78px;
}
.meta a {
        color: #fff;
}
.meta a:visited {
        color: #fff;
}
.meta a.time {
        color: inherit;
}
.meta a.time:visited {
        color: inherit;
}
.meta .time {
        display: block;
        float: right;
}
.meta img {
        height: 48px;
        position: absolute;
        left: 10px;
        border-radius: 4px;
}
.media {
        margin-top: 8px;
        margin-bottom: 8px;
        margin-left: 78px;
        height: 110px;
        overflow: hidden;
        height: 273.938px;
}
.media a {
        display: block;
        float: left;
        position: relative;
        border: 1px solid #282c37;
        box-sizing: border-box;
        overflow: hidden;
        height: 100%%;
        width: 100%%;
        cursor: zoom-in;
}
.tall {
        width: 50%% !important;
        height: 100%%;
        display: block;
}
.small {
        width: 50%% !important;
        height: 50%% !important;
        display: block;
}
.media img {
        height: 100%%;
        width: 100%%;
        -o-object-fit: cover;
        font-family: "object-fit:cover";
        object-fit: cover;
        object-position: center;
        border-radius: 4px;
}
.card {
        cursor: pointer;
        position: relative;
        display: flex;
        border: 1px solid #393f4f;
        border-radius: 4px;
        margin: 14px 0 10px 78px;
	font-size: 14px;
	color: #606984;
	text-decoration: none;
	overflow: hidden;
}

.card img {
        flex: 0 0 60px;
        width: 100%%;
	-o-object-fit: cover;
	font-family: "object-fit:cover";
	object-fit: cover;
	background-size: cover;
	background-position: 50%%;
}
.card div {
        padding: 10px 8px 8px;
        flex: 1 1 auto;
}
.card strong {
	display: block;
	font-weight: 500;
	margin-bottom: 5px;
	color: #9baec8;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
	text-decoration: none;
}
.card span {
	display: block;
	margin-top: 5px;
	font-size: 13px;
	overflow: hidden;
	text-overflow: ellipsis;
	white-space: nowrap;
}
nav a, .content a {
        color: #d9e1e8;
}
nav a:visited, .content a:visited {
        color: #d9e1e8;
}
nav {
        padding: 10px 0;
        border-top: 1px solid #393f4f;
        height: 1em;
}
footer nav {
        padding-bottom: 0;
        border-top: 1px solid #393f4f;
}
.invisible {
        display: none;
}
.emoji {
	font-family: "object-fit:contain",inherit;
	vertical-align: middle;
	-o-object-fit: contain;
	object-fit: contain;
	margin: -.2ex .15em .2ex;
	width: 16px;
	height: 16px;
}
.meta .emoji {
	height: 16px;
        position: static;
        border-radius: 0;
}
</style>
</head>
<body>
<div class="column">
<header>
<h1 class="name">%s</h1>
<div class="account">
<p class="nick">@%s</p>
<div class="bio">
%s
</div>
</div>
</header>
%s\
'''

footer_template = '''\
<footer>
%s\
<footer>
</div>
</body>
</html>
'''

nav_template = '''\
<nav>
%s\
%s\
</nav>
'''

previous_template = '''\
<a class="previous" href="%s">Later</a>
'''

next_template = '''\
<a class="next" style="float:right;" href="%s">Earlier</a>
'''

boost_template = '''\
<div class="boosted">
<a class="name" href="%s">%s</a> boosted
</div>
'''

status_template = '''\
<div class="status">
<div class="meta">
<img src="%s">
<strong class="name"><a href="%s">%s</a></strong>
<span class="nick">@%s</span>
<a class="time" href="%s">%s</a>
</div>
<div class="content">
%s
</div>
</div>
'''

media_template = '''\
<div class="media">
%s</div>\
'''

preview_template = '''\
<a href="%s" class="%s" style="padding: %s;"><img src="%s" title="%s" alt="%s" /></a>
'''

wrapper_template = '''\
<div class="wrapper">
%s%s%s%s
</div>
'''

card_template = '''\
<a href="%s" class="card" target="_blank" rel="noopener noreferrer">
<img src="%s" alt="">
<div>
<strong title="%s">%s</strong>
<span>%s</span>
</div></a>
'''

emoji_template = '''\
<img draggable="false" class="emoji" alt="%s" title="%s" src="%s">
'''

def file_url(media_dir, url1, url2=None, no_placeholder=None):
    for url in [url1, url2]:
        if url is not None:
            path = urlparse(url).path
            if os.path.isfile(media_dir + path):
                return media_dir + path
    if no_placeholder is None:
        return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADIAAAAyCAYAAAAeP4ixAAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH4QsUETQjvc7YnAAAACZpVFh0Q29tbWVudAAAAAAAQ3JlYXRlZCB3aXRoIEdJTVAgb24gYSBNYWOV5F9bAAADfElEQVRo3u1ZTUhUURg997sPy9TnDxk4IeqkmKghCKLBLNq2MCXQTXsXomFMIdK0EIoIskWLcNVKaFEulBIzxEgQLBRFXZmiaIOkboSe2Lv3tsg3+Hr96Mx7OhNzl/PuvHfPPd/5zvfdy5719Cj8B4Pwn4wkkCSQRAGilIIQ4q9zpJSQUrr6Xc2tF0kpQURgjGF2fh4zc3P4vLyMza0t27xzubkoKy1FoLYW532+yP/iBohhGHjR349P09M/qSaCUs7M/nVzE1vb23g/Po6zOTkItrcjPS0NnPOYvs9i9RGlFJ739eHj1BSI6EghY81va2nBxZKSmJiJidPvpon+wUHMzs1FwgsAGGN/3rkDz6z5T3t7sR4O/1NbnoUWA3AqJQXm/gKsHS7Iz0egrg7lZWXI1PUI6PmFBbwcGMDW9rbjXQ8eP8aznp4T1AhjICIIIVBVWYkbzc1IPX0apmnaQkXjHJXl5ai6dAmvBgbwbmzMwdSHiQlcrqmJSi+uiD0jPR3BtjZkZ2VFwkXTNMdCrQVer6/H6toaFpeWbJqamJxEoK7u+DVCRKiqqMD9UCgSQocRrJQSTQ0NNhBKKSyvrJyM2IkIvry8QwM4yM55ny++nD2alPm3rHbihnjUKiC8seEAl52VlVhFIxFhcGjIxiZjDDXV1VF7ybEz8t008SUcxsy+iR5k6drVq78ta+KOEdM0sbe3h4dPnjieNTU2QggRtX6OjREhBKSUCN69C8ZYZOeJCBeKinAlEIh/sVs7fbOz0waCc46c7Gzcam2N/w7RAtF2546ttOecI1PX0d3VFbUujg2IlBKcc7QGg7Zql3MOPSMD90MhKKVc8RVPgRARbodC4JzbQJxJTcWDe/dcA+GpRqSUeD08jG+GYauphBB41N3tWovrOSNEhDcjI46OsbOjw1Hixy0jUkqsh8OOEkTXdRTk5yfOuZZSCqtraw4gZSUliXVAp5TCzs6Oo5bK1PWY+vIT0Yhpmo6MpGmaK54RN9Vv4gPxoKHyViMAjN1dmx6EEDAMA17dKrHkjVWcDU9LlF9dnYhcd3TPnX1xacl2AEdEKPb7Uez3ewLGUyBvR0cj58La/imjv7AwcYBYYEwhbJlLKpUUezJrudGPaAeuBzTOQR46u+YViGK/39anW78lVPq1Fu0vLExsH/F60cmslQSSBHL08QPK53LVsfanXQAAAABJRU5ErkJggg=="
    return None

def text_with_emoji(media_dir, text, emojis):
    for emoji in emojis:
        path = file_url(media_dir, emoji["url"], None, True)
        if path is None:
            continue
        shortcode = ":%s:" % emoji["shortcode"]
        image = emoji_template % (
                shortcode,
                shortcode,
                path)
        text = text.replace(shortcode, image)
    return text

def write_status(fp, media_dir, status):
    boost = ""
    if status["reblog"] is not None:
        user = status["account"]
        displayname = text_with_emoji(media_dir, user["display_name"], user["emojis"])
        if not displayname:
            displayname = user["username"]
        boost = boost_template % (
            user["url"],
            displayname)
        # display the boosted status instead
        status = status["reblog"]
        
    user = status["account"]
    displayname = text_with_emoji(media_dir, user["display_name"], user["emojis"])
    if not displayname:
        displayname = user["username"]

    content = status["content"]

    if status["spoiler_text"]:
        content = "<p>%s</p>%s" % (
            status["spoiler_text"],
            status["content"])

    info = status_template % (
        file_url(media_dir, user["avatar"]),
        user["url"],
        displayname,
        user["acct"],
        status["url"],
        dateutil.parser.parse(
            status["created_at"]).strftime(
                "%Y-%m-%d %H:%M"),
        text_with_emoji(media_dir, content, status["emojis"]))

    media = ''
    attachments = status["media_attachments"]
    card = ''
    card_content = status["card"]

    if len(attachments) > 0:
        previews = []
        for attachment in attachments:
            size = ""
            padding = "0"
            if len(attachments) == 2:
                size = "tall"
                if len(previews) == 0:
                    padding = "0 1px 0 0"
                elif len(previews) == 1:
                    padding = "0 0 0 1px"
            if len(attachments) == 3:
                if len(previews) == 0:
                    padding = "0 1px 0 0"
                    size="tall"
                elif len(previews) == 1:
                    padding = "0 0 1px 1px"
                    size = "small"
                elif len(previews) == 2:
                    padding = "1px 0 0 1px"
                    size = "small"
            elif len(attachments) == 4:
                size = "small"
                if len(previews) == 0:
                    padding = "0 1px 1px 0"
                elif len(previews) == 1:
                    padding = "0 0 1px 1px"
                elif len(previews) == 2:
                     padding = "1px 1px 0 0"
                elif len(previews) == 3:
                    padding = "1px 0 0 1px"

            description = escape(attachment["description"]) if attachment["description"] is not None else ""

            previews.append(preview_template % (
                file_url(media_dir, attachment["url"]),
                size,
                padding,
                file_url(media_dir, attachment["preview_url"], attachment["url"]),
                description,
                description))

        media = media_template % (
                ''.join(previews))
    elif card_content is not None:
            card = card_template % (
                card_content["url"],
                file_url(media_dir, card_content["image"]),
                card_content["title"],
                card_content["title"],
                urlparse(card_content["url"]).netloc)

    html = wrapper_template % (boost, info, media, card)
    fp.write(html)

def html_file(domain, username, collection, page):
    return (domain + '.user.' + username + '.'
            + collection + '.' + str(page) + '.html')

def html(args):
    """
    Convert toots and media files to static HTML
    """

    toots_per_page = args.toots
    collection = args.collection
    combine = args.combine

    (username, domain) = args.user.split('@')

    status_file = domain + '.user.' + username + '.json'
    media_dir = domain + '.user.' + username
    base_url = 'https://' + domain
    data = core.load(status_file, required=True, combine=combine)
    user = data["account"]
    statuses = data[collection]

    if len(statuses) > 0:

        (pages, offset) = divmod(len(statuses), toots_per_page)
        page = 0

        while (page <= pages):

            if pages == 0:
                nav_html = ""
            else:
                if (page == 0):
                    previous_html = ""
                else:
                    previous_html = previous_template % (
                        html_file(domain, username, collection, page - 1))

                if (page < pages):
                    next_html = next_template % (
                        html_file(domain, username, collection, page + 1))
                else:
                    next_html = ""

                nav_html = nav_template % (previous_html, next_html)

            file_name = html_file(domain, username, collection, page)

            with open(file_name, mode = 'w', encoding = 'utf-8') as fp:

                print("Writing %s" % file_name)

                html = header_template % (
                    user["display_name"],
                    user["display_name"],
                    user["username"],
                    user["note"],
                    nav_html)

                # This forces UTF-8 independent of terminal capabilities, thus
                # avoiding problems with LC_CTYPE=C and other such issues.
                # This works well when redirecting output to a file, which
                # will then be an UTF-8 encoded file.
                fp.write(html)

                # Assume 184 toots, 100 toots per page:
                # page 0 is 0:84, page 1 is 84:184
                for status in statuses[
                        max(0, toots_per_page * (page - 1) + offset)
                        : toots_per_page * page + offset]:
                    write_status(fp, media_dir, status)

                fp.write(footer_template % nav_html)
                page += 1
                toots = toots_per_page
