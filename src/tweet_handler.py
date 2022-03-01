import tweepy
import os


class TweetHandler:
    def __init__(self):
        api_key = os.environ["TWITTER_API_KEY"]
        api_secret = os.environ["TWITTER_API_SECRET"]
        access_token = os.environ["TWITTER_ACCESS_TOKEN"]
        access_token_secret = os.environ["TWITTER_ACCESS_TOKEN_SECRET"]
        self.client = tweepy.Client(None, api_key, api_secret, access_token, access_token_secret)

    def post_tweet(self, text):
        self.client.create_tweet(text=text)
