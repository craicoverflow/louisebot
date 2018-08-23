#!/usr/bin/python
import praw
import os
import re
import pdb

# Grab arguments passed at script execution time
bot_name = os.getenv("ENV_BOT")
subreddit_name = os.getenv("ENV_SUBREDDIT")

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

            for submission in subreddit.new(limit=1):
                if submission.id not in posts_replied_to and submission.is_self is False:

                    # If we find at least 1 duplicate link of the current submission
                    if len(list(submission.duplicates())) > 0:

                        duplicate_list = list(submission.duplicates())

                        last_submission = duplicate_list[0] # get the most recent duplicate

                        print("{} is replying to: {}".format(bot_name, submission.permalink))

                        # form the full URL of the duplicate so we can let the poster know
                        post_url = 'https://reddit.com/r/{}/{}'.format(subreddit, last_submission.id)

                        # Reply to the current submission with a message showing them that this has already been posted.
                        submission.reply("This has been [submitted already](" + post_url + ") you lazy bastard.\n____________________________________________________________________________\n*This is an automated bot. Have feedback? Just send me a message or reply to this comment!*")
                            
                        # Add the submission ID to the list of IDs
                        posts_replied_to.append(submission.id)
                    else:
                        print('No duplicates to report this time!')
                        
    # Update the text file with the new IDs of what has been replied to
    with open("posts_replied_to.txt", "w") as f:
        for post_id in posts_replied_to:
            f.write(post_id + "\n")