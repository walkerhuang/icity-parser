#! /usr/bin/env python
# -*- coding: utf-8 -*-

import urllib
import urllib2
import requests
import re
import os


headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36'}
s = requests.session()

def get_xsrf():
    firstURL = "https://icity.ly/welcome"
    response = s.get(firstURL, headers = headers)
    pattern = re.compile(r'name="authenticity_token" value="(.*?)" />', re.S)
    token = re.findall(pattern, response.content)
    return token[0]

def get_cookies(par1):
    afterURL = "https://icity.ly/u/yyy/photos"
    loginURL = "https://icity.ly/users/sign_in"
    login = s.post(loginURL, data = par1, headers = headers)
    if login.status_code == 200:
        print "login success"
        return login.cookies
    else:
        print "failed to get cookies!"

def get_pictures(cookies, userid):
    for i in range(1, 10):
        url = "https://icity.ly/u/{0}/photos?page={1}".format(userid, i)
        directory = "./downloads/pictures/{0}".format(userid)
        if not os.path.exists(directory):
            os.makedirs(directory)

        response = s.get(url, cookies = cookies, headers = headers)

        pattern = re.compile(r'img src="(.*?)/340x340" />', re.S)
        #pattern = re.compile(r'img src="(.*?)" />', re.S)
        photos = re.findall(pattern, response.content)
        for photo in photos:
            filename = "{0}/{1}".format(directory, photo.split('/')[-1])
            if os.path.exists(filename):
                return
            with open(filename, 'wb') as the_file:
                print "downloading picture {0} from {1}".format(filename, photo)
                the_file.write(urllib.urlopen(photo).read())

def get_posts(cookies, userid):
    posts = []
    for i in range(1, 10):
        url = "https://icity.ly/u/{0}/posts?page={1}".format(userid, i)
        response = s.get(url, cookies = cookies, headers = headers)
        pattern = re.compile(r'<a class="timeago" href="/a/(.*?)">', re.S)
        posts.extend(re.findall(pattern, response.content))
    return posts

def commented_post(cookies, userid, commenterid):
    #search_str = r'<a class="user" href="/u/{0}">'.format(commenterid)
    post_file_name = "./downloads/posts/{0}".format(userid)
    searched_post = []
    if os.path.exists(post_file_name):
        with open(post_file_name, "r") as post_file:
            searched_post.extend(post_file.read().splitlines())

    search_str = r'{0}'.format(commenterid)
    commenter_pattern = re.compile(search_str)
    with open(post_file_name, "a+") as post_file:
        for post in get_posts(cookies, userid):
            if not post in searched_post:
                post_file.write(post + os.linesep)
                url = "https://icity.ly/activities/{0}".format(post)
                print "seaching " + url
                response = s.get(url, cookies = cookies, headers = headers)
                if re.findall(commenter_pattern, response.content):
                    print url

def get_friends(cokies, userid):
    url = "https://icity.ly/u/{0}/followings".format(userid)
    response = s.get(url, cookies = cookies, headers = headers)
    pattern = r'<a class="username" href="/u/(.*?)">'
    return re.findall(pattern, response.content)

authenticity_token = get_xsrf()

data = {"authenticity_token" : authenticity_token, "icty_user[login]" : "secondlife", "icty_user[password]" : "xxx", "icty_user[remember_me]" : 0}

user = "yyy"
cookies = get_cookies(data)
for f in get_friends(cookies, user):
    print "seaching friend " + f
    commented_post(cookies, f, user)
#get_pictures(cookies, user)


