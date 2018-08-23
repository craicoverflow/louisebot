#!/usr/bin/python
import praw
import os
import re
import pdb

reddit = praw.Reddit('louisebot')

subreddit = reddit.subreddit("louisebot")

if not os.path.isfile("posts_replied_to.txt"):
    posts_replied_to = []

else:
    with open("posts_replied_to.txt", "r") as f:
        posts_replied_to = f.read()
        posts_replied_to = posts_replied_to.split("\n")
        posts_replied_to = list(filter(None, posts_replied_to))

        subreddit = reddit.subreddit('louisebot')
        for submission in subreddit.new(limit=1):
            
            if submission.id not in posts_replied_to and submission.is_self is False:

                if submission.duplicates():

                    duplicate_list = list(submission.duplicates())

                    last_submission = duplicate_list[0]

                    print("louisebot is replying to: ", submission.permalink)
                    post_url = 'https://reddit.com/r/{}/{}'.format(subreddit, last_submission.id)

                    print(post_url)

                    submission.reply("This has been [submitted already](" + post_url + ") you lazy bastard.\n____________________________________________________________________________\n*This is an automated bot. Have feedback? Just send me a message or reply to this comment!*")
                    posts_replied_to.append(submission.id)

with open("posts_replied_to.txt", "w") as f:
    for post_id in posts_replied_to:
        f.write(post_id + "\n")