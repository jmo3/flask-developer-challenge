# coding=utf-8
"""
Exposes a simple HTTP API to search a users Gists via a regular expression.

Github provides the Gist service as a pastebin analog for sharing code and
other develpment artifacts.  See http://gist.github.com for details.  This
module implements a Flask server exposing two endpoints: a simple ping
endpoint to verify the server is up and responding and a search endpoint
providing a search across all public Gists for a given Github account.
"""
from __future__ import print_function

import requests, requests_cache, re
from flask import Flask, jsonify, request

# Add a requests_cache object
requests_cache.install_cache('demo_cache')

# *The* app object
app = Flask(__name__)


@app.route("/ping")
def ping():
    """Provide a static response to a simple GET request."""
    return "pong"


def gists_for_user(username):
    """Provides the list of gist metadata for a given user.

    This abstracts the /users/:username/gist endpoint from the Github API.
    See https://developer.github.com/v3/gists/#list-a-users-gists for
    more information.

    Args:
        username (string): the user to query gists for

    Returns:
        The dict parsed from the json response from the Github API.  See
        the above URL for details of the expected structure.
    """
    gists_url = 'https://api.github.com/users/{username}/gists'.format(
            username=username)
    response = requests.get(gists_url)
    # BONUS: What failures could happen?
    # BONUS: Paging? How does this work for users with tons of gists?

    return response.json()

import sys

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


@app.route("/api/v1/search", methods=['POST'])
def search():
    """Provides matches for a single pattern across a single users gists.

    Pulls down a list of all gists for a given user and then searches
    each gist for a given regular expression.

    Returns:
        A Flask Response object of type application/json.  The result
        object contains the list of matches along with a 'status' key
        indicating any failure conditions.
    """
    post_data = request.get_json()
    eprint (post_data)

    # BONUS: Validate the arguments?
    # if (post_data['username'] is None):
    #     result = {}
    #     result['status'] = 'failure: no username'
    #     result['matches'] = []
    #     return jsonify(result)
    #
    # if (post_data['pattern'] is None):
    #     result = {}
    #     result['status'] = 'failure: no pattern'
    #     result['matches'] = []
    #     return jsonify(result)

    username = post_data['username']
    pattern = post_data['pattern']

    result = {}
    gists = gists_for_user(username)

    # BONUS: Handle invalid users?
    if (gists is None):
        result = {}
        result['status'] = 'failure: invalid user'
        result['matches'] = []
        return jsonify(result)

    matches_overall = []

    for gist in gists:
        # REQUIRED: Fetch each gist and check for the pattern
        for file in gist[u'files']:
            file_content = requests.get(gists[file[u'raw_url']).json()
            matches = re.findall(pattern, file_content, re.MULTILINE)
            if matches:
                matches_overall.append(matches)

        # BONUS: What about huge gists?
        # BONUS: Can we cache results in a datastore/db?
        # DONE with requests-cache


    result['status'] = 'success'
    result['username'] = username
    result['pattern'] = pattern
    result['matches'] = matches_overall

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
