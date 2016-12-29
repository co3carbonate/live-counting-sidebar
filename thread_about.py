import live;

def thread_about():
	"Returns the live thread's about.json data, including the WebSocket (wss) URL, sidebar (resources) contents, etc."
	
	# Get websocket_url from about.json
	response = live.reddit.request(
		method = 'GET',
		path = 'live/' +live.thread+ '/about',
		params = { 'raw_json': 1 }
	);

	# Return websocket_url from response
	return response;
