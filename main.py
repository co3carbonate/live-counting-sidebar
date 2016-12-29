# External modules
import threading;
import websocket;

# Local modules
import live;
from thread_about import thread_about;
from send_update import send_update;
from websocket_message import websocket_message;

# WebSocket handling
# Connected
def on_open(ws):
	print('WebSocket connection opened');
	#send_update('Your friendly neighborhood bot has come online!');

# Disconnected
retry = True;
import time;
def on_close(ws):
	print('WebSocket connection closed');
	if retry:
		time.sleep(4);
		connect();

# Connect to WebSocket
def connect():
	"Connect to the WebSocket and call respective functions"

	# Retrieve WebSocket URL
	url = (thread_about())['data']['websocket_url'];
	print('Retrieved WebSocket URL: ' + url);

	# Setup WebSocket connection
	live.ws = websocket.WebSocketApp(
		url,
		on_open = on_open,
		on_close = on_close,
		on_message = websocket_message
	);

	# Run
	live.ws.run_forever();

# Main
# Run connect in a separate thread
thread = threading.Thread(target=connect);
thread.start();

# Receiving text input
import sys;
if __name__ == '__main__':
	while 1:
		text = input().strip();

		# Commands
		command = text.upper();

		# Exit
		if command == '--EXIT':
			retry = False;
			live.ws.close();
			sys.exit();

		else:
			send_update(text);