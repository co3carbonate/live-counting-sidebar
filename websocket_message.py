import json;

import live;
from send_update import send_update;

# Variables
new_config = None;

# Received request from WebSocket
def websocket_message(ws, message):
	"Executed when a request is received from the server"
	request = json.loads(message);

	# Only care about request_type 'update' (when an update is sent)
	if request['type'] != 'update': return;

	# Setup variables
	global new_config;	
	data = request['payload']['data']; # {body, stricken, author, created, etc.}
	body = data['body'];

	# Check for commands
	# 'sidebar status'
	if data['author'] != 'livecounting_sidebar':
		if 'sidebar status' in body:
			send_update('Online');

		# 'sidebar reset'
		if 'sidebar reset' in body:
			live.expected_count = None;
			send_update('Reset');
			print('Reset by /u/' +data['author']);

		# 'sidebar count'
		if 'sidebar count' in body:
			send_update(
				'Next expected count: ' +
				'{:,}'.format(live.expected_count)+
				'\n\nUse "sidebar reset" to reset this'
			);

		# 'sidebar config print'
		if 'sidebar config print' in body:
			send_update(
				'Current configuration:\n\n'+
				'\n'.join(
					[('    ' + line) for line in
					 json.dumps(live.special_numbers, indent = 4, sort_keys = True).split('\n')]
				)
			);

		# 'sidebar config'
		if 'sidebar config' in body:
			start = body.find('{');
			end = body.find('}');
			if start != -1 and end != -1:
				# TODO: try-except if the JSON is invalid
				# TODO: convert all values to string
				new_config = json.loads(body[start : end + 1]);
				send_update(
					'New configuration:\n\n'+
					'\n'.join(
						[('    ' + line) for line in
						 json.dumps(new_config, indent = 4, sort_keys = True).split('\n')]
					)+
					'\n\nUse "sidebar config confirm" to confirm the new configuration, or "sidebar config cancel" to cancel'
				);

		# 'sidebar config confirm'
		if 'sidebar config confirm' in body:
			if not new_config is None:
				# TODO: write to special_numbers.json
				live.special_numbers = new_config;

				send_update('Confirmed');
				print('Configuration changed to ' +json.dumps(live.special_numbers), ' by /u/' +data['author']);
				new_config = None;

		# 'sidebar config cancel'
		if 'sidebar config cancel' in body:
			if not new_config is None:
				new_config = None;
				send_update('Cancelled');


	# Detect count from the update's body
	num = '';
	for char in body:
		if char.isdigit():
			num += char;
			continue;

		elif (char == ' ' or char == ','):
			continue;

		elif(char == '~' or char == '^' or char == '#' or
			 char == '*' or char == '>' or char == '`' or
			 char == '\n'):
			# special formatting characters, only at start of str
			if len(num) == 0:
				continue;
			else:
				break;

		else:
			break;
	if len(num) == 0: return;

	# Logging
	print('{username}: {num} (expected: {expected})'
		.format(
			num = num,
			username = data['author'], 
			expected = live.expected_count
		)
	);

	# Change expected count
	# TODO: double-count handling
	if live.expected_count is None:
		live.expected_count = int(num) + 1;

	elif live.expected_count == int(num):
		live.expected_count += 1;

	else:
		# this count is false, skip remaining actions
		return;


	# Check if this number is in special_numbers
	suffix = num[-3:];
	for k, v in live.special_numbers.items():
		if suffix == v:
			# congratulate
			send_update(
				'Congratulations to /u/{username} for getting the {name} ({number}s)!'
				.format(
					username = data['author'],
					name = k,
					number = v
				)
			);

			# log
			print(
				'Detected {name} ({number}s)'
				.format(
					name = k,
					number = v
				)
			);
			
			# TODO: sidebar
			# temporary solution
			send_update(
				'/u/dominodan123 /u/TOP_20 /u/artbn: [the {num} {name}](https://www.reddit.com/live/{thread}/updates/{id})\n\n(Note: Due to the current lack of technology, I am not able to automatically update the sidebar)'
				.format(
					num = '{:,}'.format(int(num)),
					name = k,
					thread = live.thread,
					id = data['id']
				)
			);

			break;

