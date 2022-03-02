import tweepy
import os


class TweetHandler:
    def __init__(self):
        api_key = os.environ["TWITTER_API_KEY"]
        api_secret = os.environ["TWITTER_API_SECRET"]
        access_token = os.environ["TWITTER_ACCESS_TOKEN"]
        access_token_secret = os.environ["TWITTER_ACCESS_TOKEN_SECRET"]
        self.client = tweepy.Client(None, api_key, api_secret, access_token, access_token_secret)

        api_key_hotel = os.environ["TWITTER_API_KEY_HOTEL"]
        api_secret_hotel = os.environ["TWITTER_API_SECRET_HOTEL"]
        access_token_hotel = os.environ["TWITTER_ACCESS_TOKEN_HOTEL"]
        access_token_secret_hotel = os.environ["TWITTER_ACCESS_TOKEN_SECRET_HOTEL"]
        self.client_hotel = tweepy.Client(None, api_key_hotel, api_secret_hotel, access_token_hotel, access_token_secret_hotel)

    def post_tweet(self, text):
        self.client.create_tweet(text=text)

    def post_tweet_hotel(self, text):
        self.client_hotel.create_tweet(text=text)
