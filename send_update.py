import live;

# Send request to send update
def send_update(msg):
	live.reddit.request(
		method = 'POST',
		path = 'api/live/' +live.thread+ '/update',
		data = {
			'api_type': 'json',
			'body': msg
		}
	);
