#!/usr/bin/python
import praw
import os
import re
import pdb

# --------------ENVIRONMENT VARIABLES--------------
bot_name = os.getenv("ARG_BOT")
subreddit_name = os.getenv("ARG_SUBREDDIT")
arg_limit = os.getenv("ARG_LIMIT") or 10


# ---------------FUNCTIONS-----------------

# Filter the list to return only ones from the supplied subreddit
def filter_by_subreddit(seq, value):
    for el in seq:
        if el.subreddit == value: yield el

# Remove duplicates newer than the current submission
def filter_newer_duplicates(seq, submission):
    for el in seq:
        if submission.created_utc >= el.created_utc: yield el

def get_last_duplicate(submission, subreddit_name):
    duplicate_list = list(filter_by_subreddit(submission.duplicates(), subreddit_name))
    duplicate_list = list(filter_newer_duplicates(duplicate_list, submission))

    last_duplicate = None

    if len(duplicate_list):
        last_duplicate = duplicate_list[0]

    return last_duplicate
 
def reply_to_post(submission, last_submission, bot_name):
    print("{} found a repost: {}".format(bot_name, submission.permalink.encode('utf-8').strip()))

    # form the full URL of the duplicate so we can let the poster know
    post_url = 'https://reddit.com' + last_submission.permalink

    # Reply to the current submission with a message showing them that this has already been posted.
    submission.reply("This has been [submitted already](" + post_url + ") you lazy bastard.\n____________________________________________________________________________\n*This is an automated bot. Have feedback? Just send me a message or reply to this comment!*")
                                
                        # Add the submission ID to the list of IDs
    posts_replied_to.append(submission.id)

def get_posts_replied_to(f):
    posts_replied_to = f.read()
    posts_replied_to = posts_replied_to.split("\n")
    posts_replied_to = list(filter(None, posts_replied_to)) # filter the list of replied to posts so we don't go replying to the same ones again

    return posts_replied_to

def is_missing_args(bot_name, subreddit_name, limit):
    args_missing = False

    if bot_name is None or "": # We need to know the name of the bot
        print("Please provide bot name.")

        args_missing = True
    elif os.getenv is None: # We need to know the name of the subreddit to scan
        print('Please provide subreddit name.')
        
        args_missing = True
    
    return args_missing

def check_for_repost():
    with open("posts_replied_to.txt", "r") as f:

        posts_replied_to = get_posts_replied_to(f)

        subreddit = reddit.subreddit(subreddit_name)

        for submission in subreddit.new(limit = arg_limit):

            if submission.id not in posts_replied_to and submission.is_self is False:

                last_duplicate = get_last_duplicate(submission, subreddit_name)

                if last_duplicate:
                    reply_to_post(submission, last_duplicate, bot_name)
    
    # Update the text file with the new IDs of what has been replied to
    with open("posts_replied_to.txt", "w") as f:
        for post_id in posts_replied_to:
            f.write(post_id + "\n")

def init():
    if not is_missing_args(bot_name, subreddit_name, arg_limit):
        reddit = praw.Reddit(bot_name)
        subreddit = reddit.subreddit(subreddit_name)

        if not os.path.isfile("posts_replied_to.txt"):
            posts_replied_to = [] # Create an empty list to store the IDs of posts that are replied to
        else:
            check_for_repost()            
    