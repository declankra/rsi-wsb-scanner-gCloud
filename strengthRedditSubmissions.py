# relSubmissionStrength, totalSubmissions, submissionTickerMentions = strengthRedditSubmissions(stockData, recentPeriod, longerPeriod)
import pandas as pd
import praw
from datetime import datetime, timedelta

# Initialize PRAW with your Reddit app credentials
reddit = praw.Reddit(client_id='QyyiKi73QvFJqi_nX9ALQg',
                     client_secret='njKqQqY8r2JEn_V4SuWrg1uNn2FJig',
                     user_agent='fetchWSB')


def fetch_mentions(ticker, days_ago, subreddit="wallstreetbets", limit=None):
    """Fetch the number of mentions for the given ticker and time frame."""
    after_timestamp = int((datetime.now() - timedelta(days=days_ago)).timestamp())
    mentions = 0
    submissionCount = 0
    
    for submission in reddit.subreddit(subreddit).new(limit=limit):
        if submission.created_utc < after_timestamp:
            break
        submissionCount += 1
        # Check if the ticker is mentioned in either the title or the body of the submission
        if ticker.lower() in submission.title.lower() or ticker.lower() in submission.selftext.lower():
            mentions += 1
    return mentions, submissionCount


def strengthRedditSubmissions(stockData, recentPeriod, longerPeriod):

    ticker = stockData.iloc[0, 0] # If it's a DataFrame, the ticker is likely in the first row, first column
    
    """Calculate the relative strength of mentions for the given ticker."""
    # Average mentions in the longer period (30 days)
    mentions_longerPeriod, submissionCountLongerPeriod = fetch_mentions(ticker, longerPeriod)
    average_mentions_longerPeriod = mentions_longerPeriod / longerPeriod
    
    # Total mentions in the recent period (2 days)
    mentions_shorterPeriod, submissionCountShorterPeriod  = fetch_mentions(ticker, recentPeriod)
    
    # Calculate relative strength
    if average_mentions_longerPeriod > 0:
        relative_strength = mentions_shorterPeriod / average_mentions_longerPeriod
    else:
        relative_strength = 0  # To avoid division by zero
    
    relSubmissionStrength = relative_strength
    totalSubmissions = submissionCountLongerPeriod
    submissionTickerMentions = mentions_shorterPeriod
    
    
    return relSubmissionStrength, totalSubmissions, submissionTickerMentions