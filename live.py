# Global variables
import praw;

# Special numbers dictionary
import json;
special_numbers = {};

with open('special_numbers.json') as json_file:
	special_numbers = json.load(json_file);
	print('Retrieved special_numbers.json');

# Next expected count
expected_count = None;

# Reddit API (PRAW)
# User authentication
reddit = praw.Reddit(
	client_id = '', # FILL THIS UP ACCORDINGLY
	client_secret = '',
	username = '',
	password = '',
	user_agent = ''
);

# Live thread
thread = 'ta535s1hq2je';

# WebSocket
ws = None;


# Global functions
from send_update import send_update;

def on_open(ws):
	print('WebSocket connection opened');
	send_update('Your friendly neighborhood bot has come online!');

def on_close(ws):
	print('WebSocket connection closed');