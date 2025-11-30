# Python standard libraries
import json

# Third-party libs
from flask import(
    Blueprint,
    redirect,
    request,
    url_for
)

from flask_login import(
    login_required,
    login_user,
    logout_user
)

from oauthlib.oauth2 import WebApplicationClient
import requests

# Internal imports
from .config import(
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_DISCOVERY_URL
)

from .user import User
from . import client

# Auth blueprint setup
auth_google = Blueprint('auth_google', __name__)

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@auth_google.route('/login')
def login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg['authorization_endpoint']

    # Use library to construct the request for Google login and
    # provide scopes that let you retrieve users's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri = request.base_url + '/callback',
        scope = ['openid', 'email', 'profile'],
    )
    return redirect(request_uri)

@auth_google.route('/login/callback')
def callback():
    # Get authorixation code Google sent back to you
    code = request.args.get('code')

    # Find out what URL to hit to get tokens that allow you to
    # ask for rhings on behalf of the user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg['token_endpoint']

    # Prepare and send a request to het tokens
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response = request.url,
        redirect_url = request.base_url,
        code = code
    )
    token_response = requests.post(
        token_url,
        headers = headers,
        data = body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)
    )

    # Parse the tokens
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that we have tokens let's find and hit the URL
    # from Google that gives you the user's profile information
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg['userinfo_endpoint']
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers = headers, data = body)

    # Make sure user email is verified
    # The user authenticated with Google, authorized our app
    # and now we've verified their email through Google
    if userinfo_response.json().get('email_verified'):
        unique_id = userinfo_response.json()['sub']
        users_email = userinfo_response.json()['email']
        picture = userinfo_response.json()['picture']
        users_name = userinfo_response.json()['given_name']
    else:
        return 'User email not available or not verified by Google.', 400

    # Create a user in our db with the information provided by Google
    user = User(
        id_ = unique_id,
        name = users_name,
        email = users_email,
        profile_pic = picture
    )

    # Doesn't exist? Add it to the databse
    if not User.get(unique_id):
        User.create(
            unique_id,
            users_name,
            users_email,
            picture
        )

    # Begin user session by logging the user in
    login_user(user)

    # Send user back to homepage
    return redirect(url_for('main.index'))

@auth_google.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
