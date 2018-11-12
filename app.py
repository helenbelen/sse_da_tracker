import flask
from flask import Flask, render_template, make_response, request
import os
import requests
import json
import re
import datetime
from datetime import date
import csv
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
import oauth2client
from oauth2client.client import OAuth2WebServerFlow
import sys

app = Flask(__name__)

# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'


# Note: A secret key is included in the sample so that it works.
# If you use this code in your application, replace this with a truly secret
# key. See http://flask.pocoo.org/docs/0.12/quickstart/#sessions.
app.secret_key = os.urandom(24)


@app.route("/")
def index():
  video_list = {}
  selected = {}
  message = " "
  nextPage = False
  prevPage = False
  firstPage = False
  showPrevButton = False
  showNextButton = False

  if 'credentials' in flask.session:
    try:
      if 'prevPage' in flask.session and 'page_request' in flask.session and flask.session['page_request'] == "previous":
          prevPage = True 
                        
      elif 'nextPage' in flask.session and 'page_request' in flask.session and flask.session['page_request'] == "next":
          nextPage = True
      else:
          firstPage = True
     
     
      flask.session['tabledata'] = api_request(firstPage,prevPage,nextPage)
      video_list = flask.session['tabledata']
      if 'selected_onpage' in flask.session:
        selected = flask.session['selected_onpage']

      message = "Table Updated From API On " + datetime.datetime.strftime(date.today(),'%m-%d-%Y')
     
      if 'prevPage' in flask.session and flask.session['prevPage'] is not None:
        showPrevButton = True
     
      if 'nextPage' in flask.session and flask.session['nextPage'] is not None:
        showNextButton = True
      
    except:
      message = "Error: " + str(sys.exc_info())
      if 'tabledata' in flask.session:
        video_list = flask.session['tabledata']
        message += "- Using Session Data."
      else:
        video_list = {}
        message += " - No Videos In Session Data"

    return render_template('index.html', logged_in = True, videos = video_list, message = message, prevPage= showPrevButton, nextPage= showNextButton,selected =selected)

  else:
    return render_template('index.html', logged_in = False, videos = video_list, message = message, prevPage= showPrevButton, nextPage= showNextButton,selected =selected)

 

@app.route('/authorize')
def authorize():
  # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
  
  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES)

  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

  authorization_url, state = flow.authorization_url(
      # Enable offline access so that you can refresh an access token without
      # re-prompting the user for permission. Recommended for web server apps.
      access_type='offline',
      # Enable incremental authorization. Recommended as a best practice.
      include_granted_scopes='true')

  # Store the state so the callback can verify the auth server response.
  flask.session['state'] = state

  return flask.redirect(authorization_url)



@app.route('/oauth2callback')
def oauth2callback():
  # Specify the state when creating the flow in the callback so that it can
  # verified in the authorization server response.
  state = flask.session['state']

  
  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

  # Use the authorization server's response to fetch the OAuth 2.0 tokens.
  authorization_response = flask.request.url
  flow.fetch_token(authorization_response=authorization_response)

  # Store credentials in the session.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  credentials = flow.credentials
  flask.session['credentials'] = credentials_to_dict(credentials)
  
  return flask.redirect(flask.url_for('index'))


@app.route('/revoke')
def revoke():
  if 'credentials' not in flask.session:
    return ('You need to <a href="/authorize">authorize</a> before ' +
            'testing the code to revoke credentials.')

  credentials = google.oauth2.credentials.Credentials(
    **flask.session['credentials'])

  revoke = requests.post('https://accounts.google.com/o/oauth2/revoke',
      params={'token': credentials.token},
      headers = {'content-type': 'application/x-www-form-urlencoded'})

  status_code = getattr(revoke, 'status_code')
  if status_code == 200:
    app.logger.debug('Credentials successfully revoked.')
    
  else:
    app.logger.debug('An error occurred.')
  
  clear_credentials()
  return flask.redirect(flask.url_for('index'))

@app.route('/download-file', methods=['POST'])
def download():
  flask.session['selected_csvdata'] = request.json['data']

  if 'csvdata' and 'selected_csvdata' in flask.session:
    return write_csv(flask.session['selected_csvdata'],flask.session['csvdata'])
   
  return flask.redirect(flask.url_for('index'))


@app.route('/page',methods=['POST'])
def page_request():
  
  flask.session['page_request'] = request.json['data']
  flask.session['selected_onpage'] = request.json['selected'];
  
  return request.json['data']


def api_request(firstPage,prevPage,nextPage):
  if 'credentials' not in flask.session:
    return flask.redirect('authorize')

  # Load credentials from the session.
  credentials = google.oauth2.credentials.Credentials(
      **flask.session['credentials'])

  youtube = googleapiclient.discovery.build(
    API_SERVICE_NAME, API_VERSION, credentials=credentials)
  

  if firstPage:
    playlist = youtube.videos().list(
      part ='snippet,contentDetails',
      myRating ='like',
      maxResults = 25).execute()
  elif prevPage:
    playlist = youtube.videos().list(
      part ='snippet,contentDetails',
      myRating ='like',
      maxResults = 25,
      pageToken = flask.session['prevPage']).execute()
  elif nextPage:
    playlist = youtube.videos().list(
      part ='snippet,contentDetails',
      myRating ='like',
      maxResults = 25,
      pageToken = flask.session['nextPage']).execute()


  # Save credentials back to session in case access token was refreshed.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  flask.session['credentials'] = credentials_to_dict(credentials)
  mylist = {}
  mylist = playlist
  
  return process_data(mylist)

def process_data(a_list):
  processed_list = {}
  csv_list = {} 
  
  try :
    flask.session['nextPage'] = a_list['nextPageToken']
      
  except:
    flask.session['nextPage'] = None
      
  try:
    flask.session['prevPage'] = a_list['prevPageToken']
      
  except:
    flask.session['prevPage'] = None
      
  for video in a_list['items']:
      newdate = datetime.datetime.strptime(
        video['snippet']['publishedAt'], 
        "%Y-%m-%dT%H:%M:%S.000Z")
      d = datetime.datetime.strftime(newdate,"%m-%d-%Y %H:%M")

      mydur = re.findall(
        '[0-9]+',video['contentDetails']['duration'], 
        flags=re.IGNORECASE)
      tags = [" Day(s)"," Hour(s)"," Minutes"," Seconds"]
      conv = [1440,60,1,(1/60)]

      if len(mydur) == 1:
        sub_tags = tags[3]
        sub_conv = conv[3]
      if len(mydur) == 2:
        sub_tags = tags[2:]
        sub_conv = conv[2:]
      if len(mydur) == 3:
        sub_tags = tags[1:]
        sub_conv= conv[1:]
      if len(mydur) == 4:
        sub_tags = tags
        sub_conv = conv

      dur_list = [mydur[i] + sub_tags[i] for i in range(0,len(mydur))]

      processed_list[d] = [video['snippet']['title'].replace(",",""),dur_list]

      minute_list = [ int(int(mydur[i]) * sub_conv[i]) for i in range(0,len(mydur))]
      
      total_minutes = 0
      for i in minute_list:

        total_minutes += i

      csv_list[d] = [video['snippet']['title'].replace(",",""),total_minutes]
      
  if 'csvdata' in flask.session:
    flask.session['csvdata'].update(csv_list)
  else:
    flask.session['csvdata'] = csv_list

  return processed_list

def write_csv(selected_rows, rows):
  
  overall_total = 0
  mydate = date.today()
  filename = 'DARport-'+str(mydate)+'.csv'


  csv = 'date,title,duration\n'
  for key,value in rows.items():
    if key in selected_rows:
      overall_total += value[1]
      csv += key +',' + value[0] +','+ str(value[1]) + '\n'
      
  csv += ' ,Total,' + str(overall_total) +'\n'

  return csv

def clear_credentials():
  if 'credentials' in flask.session:
    del flask.session['credentials']
    if 'selected_onpage' in flask.session:
      del flask.session['selected_onpage']
    app.logger.debug ('Credentials have been cleared.<br><br>')

  return flask.redirect(flask.url_for('index'))


def credentials_to_dict(credentials):

  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

if __name__ == "__main__":
	# When running locally, disable OAuthlib's HTTPs verification.
  # ACTION ITEM for developers:
  #     When running in production *do not* leave this option enabled.
  #os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

  # Specify a hostname and port that are set as a valid redirect URI
  # for your API project in the Google API Console.
  app.run('localhost', 8080, debug=False)
