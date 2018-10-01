#!/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import date

def filter(duplicate_list, submission_created_utc, subreddit_name, max_age):
    created_at = date.fromtimestamp(submission_created_utc)

    for duplicate in duplicate_list:
        duplicate_created_at = date.fromtimestamp(duplicate.created_utc)
        
        days_difference = (created_at - duplicate_created_at).days

        if (duplicate.subreddit == subreddit_name and days_difference <= max_age and 
            submission_created_utc > duplicate.created_utc): 
            yield duplicate

def last(submission, subreddit_name, max_age):

    duplicate_list = list(filter(submission.duplicates(), submission.created_utc, subreddit_name, max_age))

    last_duplicate = None

    if len(duplicate_list):
        last_duplicate = duplicate_list[0]

    return last_duplicate