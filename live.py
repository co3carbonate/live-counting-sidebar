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

# Who said the last valid count (to prevent double counting)
last_counter = None;

# Reddit API (PRAW)
# User authentication
reddit = praw.Reddit(
	client_id = '',
	client_secret = '',
	username = '',
	password = '',
	user_agent = ''
);

# Live thread information
thread = 'ta535s1hq2je';

# WebSocket
ws = None;
