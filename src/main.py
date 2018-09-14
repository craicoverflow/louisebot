#!/usr/bin/python
# -*- coding: utf-8 -*-
import praw
import os
import re
import sys
import pdb
import argparse
import duplicates
from datetime import datetime
from configparser import ConfigParser
from collections import defaultdict
from io import StringIO

def load_config():
    default = defaultdict(str)
    default["bot"] = "ThatsARepostBot"
    default["subreddit"] = "thats_a_repost_bot"
    default["limit"] = "25"
    default["maxage"] = "100"
    default["logsdir"] = "logs"

    config_path = os.path.expanduser("./config/default.rc")
    section_name = "root"
    try:
        config = ConfigParser(default)
        with open(config_path, "r") as stream:
            stream = StringIO("[{section_name}]\n{stream_read}"
            .format(section_name=section_name, stream_read=stream.read()))

            if sys.version_info >= (3, 0):
                config.read_file(stream)
            else:
                config.readfp(stream)

            ret = {}

            def add_to_ret(fun, name):
                try:
                    ret[name] = fun(section_name, name)
                except ValueError as e:
                    err_string = "Error in config file. Variable '{}': {}. The default '{}' will be used."

                    # print sys.stderr >> err.str_format(name, str(e), default[name])
                    ret[name] = default[name]

            add_to_ret(config.get, "bot")
            add_to_ret(config.get, "subreddit")
            add_to_ret(config.getint, "limit")
            add_to_ret(config.getint, "maxage")
            add_to_ret(config.get, "logsdir")

            return ret
        
    except IOError as e:
        return default

config = load_config()

def parse_args():
    parser = argparse.ArgumentParser(description = "Your friendly neighbourhood repost checking robot!")
    parser.add_argument("-b", "--bot", type=str, default=config["bot"])
    parser.add_argument("-s", "--subreddit", type=str, default=config["subreddit"])
    parser.add_argument("-l", "--limit", type=int, default=config["limit"])
    parser.add_argument("-m", "--maxage", type=int, default=config["maxage"])
    parser.add_argument("-d", "--logsdir", type=str, default=config["logsdir"])

    args = parser.parse_args()
    return args

def get_posts_replied_to(f):
    posts_replied_to = f.read()
    posts_replied_to = posts_replied_to.split("\n")
    posts_replied_to = list(filter(None, posts_replied_to)) # filter the list of replied to posts so we don't go replying to the same ones again

    return posts_replied_to

if __name__ == '__main__':

    args = parse_args()

    subreddit_name = args.subreddit
    limit = args.limit
    bot_name = args.bot
    max_age = args.maxage
    logs_dir = args.logsdir

    reddit = praw.Reddit(bot_name)
    subreddit = reddit.subreddit(subreddit_name)

    with open("{}/daily.log".format(logs_dir), "w+") as log:
        log.write("Subreddit: {} [{}]\n".format(subreddit_name, datetime.utcnow()))
    
    if not os.path.isfile("{}/posts_replied_to.txt".format(logs_dir)):
        posts_replied_to = [] # Create an empty list to store the IDs of posts that have been replied to
    else:
        with open("{}/posts_replied_to.txt".format(logs_dir), "r") as f:

            posts_replied_to = get_posts_replied_to(f)

            for submission in subreddit.new(limit = limit):

                if submission.id not in posts_replied_to and submission.is_self is False:

                    latest_duplicate = duplicates.last(submission, subreddit_name, max_age)

                    if latest_duplicate:

                        # form the full URL of the duplicate so we can let the poster know
                        post_url = 'https://reddit.com' + latest_duplicate.permalink

                        source_code_url = "https://github.com/craicoverflow/thats_a_repost_bot"
                        # Reply to the current submission with a message showing them that this has already been posted.
                        submission.reply("This has been [submitted already](" + post_url + ") you lazy bastard.\n____________________________________________________________________________\n*This is an automated bot. Have feedback? Just send me a message or reply to this comment! Here is my [source code](" + source_code_url + ").*")
                                
                        # Add the submission ID to the list of IDs
                        posts_replied_to.append(submission.id)

    # Update the text file with the new IDs of what has been replied to
    with open("{}/posts_replied_to.txt".format(logs_dir), "w") as f:
        for post_id in posts_replied_to:
            f.write(post_id + "\n")
