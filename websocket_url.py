import live;

def websocket_url():
	"Returns the WebSocket (wss) URL, from about.json of the live thread"

	# Get websocket_url from about.json
	response = live.reddit.request(
		method = 'GET',
		path = 'live/' +live.thread+ '/about',
	);

	# Return websocket_url from response
	return response['data']['websocket_url'];
