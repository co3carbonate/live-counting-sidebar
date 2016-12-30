import threading;
import time;

import live;

# Send request to delete update
def delete_update(update_id, wait = 0):
	if wait > 0:
		# Run the same function without wait, but in a new thread
		time.sleep(wait);

	live.reddit.request(
		method = 'POST',
		path = 'api/live/' +live.thread+ '/delete_update',
		data = {
			'api_type': 'json',
			'id': update_id
		}
	);
