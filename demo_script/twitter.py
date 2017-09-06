

from urllib2 import urlopen, Request, HTTPError


import base64
import json
import logging
import werkzeug


_logger = logging.getLogger(__name__)

API_ENDPOINT = 'https://api.twitter.com'
API_VERSION = '1.1'

URLOPEN_TIMEOUT = 10

config = {
    'twitter_consumer_key': 'FnR7OU3Se8Ev86duPERszaERS',
    'twitter_consumer_secret_key': 'PlAWSdrlAKVTkEaNNTH7rCR5o81GqPLViCAewrSGrH6Sx6pO6o'
}

access_token = None


def _get_access_token():
    global access_token
    request_url = '%s/oauth2/token' % API_ENDPOINT
    bearer_token = '%s:%s' % (
        config.get('twitter_consumer_key'),
        config.get('twitter_consumer_secret_key'))
    encoded_token = base64.b64encode(bearer_token)
    request = Request(request_url)
    request.add_header('Content-Type',
                       'application/x-www-form-urlencoded;charset=UTF-8')
    request.add_header('Authorization', 'Basic %s' % encoded_token)
    request.add_data('grant_type=client_credentials')
    data = json.load(urlopen(request, timeout=URLOPEN_TIMEOUT))
    access_token = data['access_token']
    print "received token ====", access_token
    return access_token


def _request(url, params=None):
    # access_token = _get_access_token()
    if params:
        params = werkzeug.url_encode(params)
        url = url + '?' + params
    try:
        print url
        request = Request(url)
        request.add_header('Authorization', 'Bearer %s' % access_token)
        response = json.load(urlopen(request))
        return response
    except HTTPError, e:
        _logger.debug("Twitter API request failed with code: %r, msg: %r, content: %r",
                      e.code, e.msg, e.fp.read())
        raise

def _request_next_page(url, params=None, next_cursor=None):
    params['cursor'] = next_cursor
    return _request(url, params)

def get_followers():

    count = 0
    follower_url = '%s/%s/followers/ids.json' % (
        API_ENDPOINT, API_VERSION)
    params = {
        'screen_name': 'issahilkhattar',
        'count': 5000
    }
    response = _request(follower_url, params=params)
    count += len(response['ids'])
    while response.get('next_cursor'):
        response = _request_next_page(
            follower_url, params=params, next_cursor=response.get('next_cursor'))
        count += len(response['ids'])
    print "Total Follwers of `%s` is %s " % (params['screen_name'], count)

    return response


def get_followings():

    count = 0
    follower_url = '%s/%s/friends/ids.json' % (
        API_ENDPOINT, API_VERSION)
    params = {
        'screen_name': 'sindhav21',
        'count': 5000
    }
    response = _request(follower_url, params=params)
    count += len(response['ids'])
    while response.get('next_cursor'):
        print "=====next cursor===", response.get('next_cursor')
        response = _request_next_page(
            follower_url, params=params, next_cursor=response.get('next_cursor'))
        count += len(response['ids'])
    print "Total Following of `%s` is %s " % (params['screen_name'], count)

    return response


def get_tweets():
    count = 0
    follower_url = '%s/%s/statuses/user_timeline.json' % (
        API_ENDPOINT, API_VERSION)
    params = {
        'screen_name': 'sindhav21',
        'count': 10,
        'include_rts': False    # 'dont' include retweets
    }
    response = _request(follower_url, params=params)
    counter = 1
    count = len(response)
    for tweet in response:
        print ">>>>>> Tweet No. ", counter
        print tweet['text']
        counter += 1

    print "Total Twitts of `%s` is %s " % (params['screen_name'], count)
    return response


if __name__ == "__main__":

    _get_access_token()
    # get_followers()
    # get_followings()
    get_tweets()
