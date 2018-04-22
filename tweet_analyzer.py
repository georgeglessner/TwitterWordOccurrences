#!/usr/bin/env python

# -*- coding: UTF-8 -*-
''' 

Find the most common words in a user's Twitter feed 

Usage: 
    tweet_analyzer [--user USER] [--num NUMBER OF OCCURENCES]

Options:
    -h --help       show this
    -u --user       username of account to analyze
    -n --num        minimum number of occurences the word appears [default: 20]             

'''

import string
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn
from twitter_scraper import get_tweets
from collections import defaultdict
import tweepy
from credentials import *
import csv
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-u', '--user', type=str, help='username of account to analyze')
    parser.add_argument(
        '-n',
        '--num',
        type=int,
        help='minimum number of occurences the word appers [default: 20]')

    args = parser.parse_args()

    if args.user:
        user = '@' + args.user
    else:
        user = input('Username to analyze: ')
        user = '@' + user

    if args.num:
        num_occurences = int(args.num)
    else:
        num_occurences = 20

    tweets = []
    count = dict()
    total_tweets_analyzed = 0

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)

    print('\nAnalyzing tweets. This could take a few seconds.')

    # get tweets from user's timeline
    for tweet in tweepy.Cursor(api.user_timeline, screen_name=user).items():
        tweets.append(tweet._json['text'].lower())

    # get rid of common words
    for tweet in tweets:
        total_tweets_analyzed += 1
        for word in tweet.split(' '):
            words = nltk.word_tokenize(word.replace("'", ""))
            stop_words = stopwords.words('english') + list(
                string.punctuation) + ['“', '”']
            filtered_words = [word for word in words if word not in stop_words]

            if len(filtered_words) > 0:
                if filtered_words[0] not in [
                        'https',
                        '``',
                        '...',
                        'http',
                        'rt',
                ]:
                    if filtered_words[0] in count:
                        count[filtered_words[0]] += 1
                    else:
                        count[filtered_words[0]] = 1

    # create a csv file with the results
    with open('results.csv', 'w') as file:
        output = csv.writer(file)
        output.writerow(['Word occurences in tweets by ' + user])
        output.writerow(['Word', '# of Occurences'])
        for result in count:
            if count.get(result) > num_occurences and len(result) > 1:
                output.writerow([result, str(count.get(result))])

    print('Completed! Total tweets analyzed: {}'.format(total_tweets_analyzed))


if __name__ == '__main__':
    main()
