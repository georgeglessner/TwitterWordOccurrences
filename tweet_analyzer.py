#!/usr/bin/env python

# -*- coding: UTF-8 -*-
''' 

Find the most common words in a user's Twitter feed 

Usage: 
    tweet_analyzer [--user USER] [--num NUMBER OF OCCURRENCES] [-f OUTPUTFILE]

Options:
    -h --help       show this
    -u --user       username of account to analyze
    -n --num        minimum number of occurrences the word appears [default: 20]    
    -f --file       name of output file (.csv) [default: results.csv]         

'''

import string
import nltk
import tweepy
import csv
import argparse
from credentials import consumer_key
from credentials import consumer_secret
from credentials import access_token
from credentials import access_token_secret
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn
from collections import defaultdict


def main():
    # add arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-u', '--user', type=str, help='username of account to analyze')
    parser.add_argument(
        '-n',
        '--num',
        type=int,
        help='minimum number of occurrences the word appers [default: 20]',
        default=20)
    parser.add_argument(
        '-f',
        '--file',
        type=str,
        help='name of output file (.csv)',
        default='results.csv')

    args = parser.parse_args()

    # parse arguments
    if args.user:
        user = '@' + args.user
    else:
        user = input('Username to analyze: ')
        user = '@' + user

    if args.num:
        num_occurrences = int(args.num)

    if args.file:
        if '.csv' not in args.file:
            output_file = args.file + '.csv'
        else:
            output_file = args.file

    tweets = []  # list of tweets obtained from user timeline
    count = defaultdict(int)
    total_tweets_analyzed = 0
    total_results = 0

    # make connection
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True)

    print('\nAnalyzing tweets. This could take a few seconds...')

    # get tweets from user's timeline
    for tweet in tweepy.Cursor(api.user_timeline, screen_name=user).items():
        tweets.append(tweet._json['text'].lower())

    # get rid of stop words
    # list of stop words https://gist.github.com/sebleier/554280
    stop_words = stopwords.words('english') + list(
        string.punctuation) + ['“', '”']

    # words to ignore in results
    BACKLIST_WORDS = [
        'https',
        '``',
        '...',
        'http',
        'rt',
    ]

    # analyze tweets
    for tweet in tweets:
        total_tweets_analyzed += 1
        for word in tweet.split(' '):
            words = nltk.word_tokenize(word.replace("'", ""))
            filtered_words = [word for word in words if word not in stop_words]

            if len(filtered_words) > 0:
                if filtered_words[0] not in BACKLIST_WORDS:
                    count[filtered_words[0]] += 1

    # create a csv file with the results
    with open(output_file, 'w') as file:
        output = csv.writer(file)
        output.writerow(['Word occurrences in tweets by ' + user])
        output.writerow(['Word', '# of Occurrences'])
        for result in count:
            if count.get(result) > num_occurrences and len(result) > 1:
                output.writerow([result, str(count.get(result))])
                total_results += 1

    print(f'\nCompleted! Total tweets analyzed: {total_tweets_analyzed}')
    print(f'Total results found: {total_results}')


if __name__ == '__main__':
    main()
