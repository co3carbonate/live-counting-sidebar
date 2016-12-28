# External modules
import threading;
import websocket;

# Local modules
import live;
from websocket_url import websocket_url;
from websocket_message import websocket_message;
from send_update import send_update;

# Connect to WebSocket
def connect():
	"Connect to the WebSocket and call respective functions"

	# Retrieve Websocket URL
	url = websocket_url();
	print('Retrieved WebSocket URL: ' + url);

	# Setup WebSocket connection
	live.ws = websocket.WebSocketApp(
		url,
		on_open = live.on_open,
		on_close = live.on_close,
		on_message = websocket_message
	);

	# Run
	live.ws.run_forever();

# Main
def main():
	# Run connect in a separate thread
	thread = threading.Thread(target=connect);
	thread.start();

main();

# Receiving text input
if __name__ == '__main__':
	while 1:
		text = input().strip();

		# Commands
		command = text.upper();

		# Exit
		if command == '--EXIT':
			live.ws.close();
			quit();

		else:
			send_update(text);