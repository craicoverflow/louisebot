#!/usr/bin/python
import praw
import os
import re
import pdb

# Grab arguments passed at script execution time
bot_name = os.getenv("ENV_BOT")
subreddit_name = os.getenv("ENV_SUBREDDIT")

def filter_by_subreddit(seq, value):
    for el in seq:
        if el.subreddit == value: yield el

def filter_newer_duplicates(seq, submission):
    for el in seq:
        if submission.created_utc >= el.created_utc: yield el

if bot_name is None: # We need to know the name of the bot
    print('Please provide bot name.')
elif subreddit_name is None: # We need to know the name of the subreddit to scan
    print('Please provide subreddit name.')
else:
    reddit = praw.Reddit(bot_name)
    subreddit = reddit.subreddit(subreddit_name)

    if not os.path.isfile("posts_replied_to.txt"):
        posts_replied_to = [] # Create an empty list to store the IDs of posts that are replied to
    else:
        with open("posts_replied_to.txt", "r") as f:
            posts_replied_to = f.read()
            posts_replied_to = posts_replied_to.split("\n")
            posts_replied_to = list(filter(None, posts_replied_to)) # filter the list of replied to posts so we don't go replying to the same ones again

            subreddit = reddit.subreddit(subreddit_name)

            for submission in subreddit.new(limit=10):

                if submission.id not in posts_replied_to and submission.is_self is False:

                    duplicate_list = list(filter_by_subreddit(submission.duplicates(), subreddit_name))
                    duplicate_list = list(filter_newer_duplicates(duplicate_list, submission))

                    # If we find at least 1 duplicate link of the current submission
                    if len(duplicate_list) > 0:

                        last_submission = duplicate_list[0] # get the most recent duplicate
                        
                        print("{} found a repost: {}".format(bot_name, submission.permalink.encode('utf-8').strip()))

                        # form the full URL of the duplicate so we can let the poster know
                        post_url = 'https://reddit.com' + last_submission.permalink

                        print('\n')
                        # Reply to the current submission with a message showing them that this has already been posted.
                        submission.reply("This has been [submitted already](" + post_url + ") you lazy bastard.\n____________________________________________________________________________\n*This is an automated bot. Have feedback? Just send me a message or reply to this comment!*")
                                
                        # Add the submission ID to the list of IDs
                        posts_replied_to.append(submission.id)

    # Update the text file with the new IDs of what has been replied to
    with open("posts_replied_to.txt", "w") as f:
        for post_id in posts_replied_to:
            f.write(post_id + "\n")