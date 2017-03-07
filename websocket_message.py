import threading;
import json;

import live;
from thread_about import thread_about;
from send_update import send_update;
from delete_update import delete_update;

# Variables
json_error_str = 'Error parsing JSON configuration.\n\n(Please check that you had used double quotes ["], and not single quotes [\'].)';
new_config = None;

# Received request from WebSocket
def websocket_message(ws, message):
	"Executed when a request is received from the server"
	request = json.loads(message);

	# Only care about request_type 'update' (when an update is sent)
	if request['type'] != 'update': return;

	# Setup variables
	global json_error_str;
	global new_config;	
	data = request['payload']['data']; # {body, stricken, author, created, etc.}
	body = data['body'];

	# Check for commands
	if data['author'] != 'livecounting_sidebar':
		# 'sidebar help'
		if 'sidebar help' in body:
			send_update('[Information about me](https://www.reddit.com/r/livecounting_sidebar/wiki/index)');

		# 'sidebar status'
		elif 'sidebar status' in body:
			send_update('Online');

		# 'sidebar reset' / 'count_better reset'
		elif 'sidebar reset' in body or 'count_better reset' in body:
			live.expected_count = None;
			live.last_counter = None;
			print('Reset by /u/' +data['author']);
			
			if 'count_better reset' in body:
				send_update('I will reset together with my fellow brethren');

		# 'sidebar count'
		elif 'sidebar count' in body:
			send_update(
				'Next expected count: ' +
				'{:,}'.format(live.expected_count)+
				'\n\nUse "sidebar reset" to reset this'
			);

		# 'sidebar config print'
		elif 'sidebar config print' in body:
			send_update(
				'Current configuration:\n\n'+
				'\n'.join(
					[('    ' + line) for line in
					 json.dumps(live.special_numbers, indent = 4, sort_keys = True).split('\n')]
				)
			);

		# The following commands are only usable by a few people
		elif(data['author'] == 'TOP_20' or
			 data['author'] == 'co3_carbonate' or		
			 data['author'] == 'KingCaspianX' or		
			 data['author'] == 'rschaosid' or		
			 data['author'] == 'artbn' or
			 data['author'] == 'NumberOfTheDayBot'):		

			# 'sidebar config confirm'
			if 'sidebar config confirm' in body:
				if not new_config is None:
					live.special_numbers = new_config;
					
					# write to special_numbers.json
					json_str = json.dumps(live.special_numbers);
					with open('special_numbers.json', 'w') as json_file:
						json_file.write(json_str);

					send_update('Confirmed');
					print('Configuration changed to ' +json_str, ' by /u/' +data['author']);
					new_config = None;

			# 'sidebar config cancel'
			elif 'sidebar config cancel' in body:
				if not new_config is None:
					new_config = None;
					send_update('Cancelled');

			# 'sidebar config'
			elif 'sidebar config' in body:
				start = body.find('{');
				end = body.find('}');
				if start != -1 and end != -1:
					try:
						new_config = json.loads(body[start : end + 1]);
					except:
						# in case of invalid JSON
						send_update(json_error_str);
						return;

					# convert all JSON values to string
					for k, v in new_config.items():
						new_config[k] = str(v);

					# announce
					send_update(
						'New configuration:\n\n'+
						'\n'.join(
							[('    ' + line) for line in
							 json.dumps(new_config, indent = 4, sort_keys = True).split('\n')]
						)+
						'\n\nUse "sidebar config confirm" to confirm the new configuration, or "sidebar config cancel" to cancel'
					);
				else:
					send_update(json_error_str);
	else:
		# This was posted by livecounting_sidebar, delete after some time
		thread = threading.Thread(target=lambda: delete_update(data['name'], 60));
		thread.start();
		return;

	# Detect count from the update's body
	# (TODO: use the same system as count_better)
	num = '';
	for char in body:
		if char.isdigit():
			num += char;
			continue;

		elif (char == ' ' or char == ',' or char == '.'):
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
	if live.expected_count is None:
		live.expected_count = int(num) + 1;
		live.last_counter = data['author'];

	elif data['author'] == live.last_counter:
		# double counting, skip
		return;

	elif live.expected_count == int(num):
		live.expected_count += 1;
		live.last_counter = data['author'];

	else:
		# this count is false, skip remaining actions
		return;


	# Check if this number is in special_numbers
	suffix = num[-3:];
	for k, v in live.special_numbers.items():
		if suffix == v:
			# congratulate
			send_update(
				'Congratulations to {username} for getting the {name} ({number}s)!'
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
			
			# Now, the most important - actually updating the sidebar
			# (old method when the tech was still shitty)
			"""send_update(
				'/u/dominodan123 /u/TOP_20 /u/artbn7: the [{num}](https://www.reddit.com/live/{thread}/updates/{id}) {name} by {username}\n\n(Note: Due to the current lack of technology, I am not able to automatically update the sidebar)'
				.format(
					num = '{:,}'.format(int(num)),
					name = k,
					username = data['author'],
					thread = live.thread,
					id = data['id']
				)
			);"""

			# Get latest thread info, especially the sidebar contents
			thread_info = (thread_about())['data'];
			sidebar_contents = thread_info['resources'];

			# Generate the sidebar_id from the name
			sidebar_id = '[](#sidebar_' + ('_'.join(k.upper().split())) + ')';
			
			# Find index of the character immediately after sidebar_id in sidebar_contents
			index = sidebar_contents.find(sidebar_id) 
			if index == -1: break;
			index += len(sidebar_id);

			# Increment index until a non-whitespace character
			loop_broke = False;
			for i in range(index, len(sidebar_contents)):
				if sidebar_contents[i].isspace():
					index += 1;
				else:
					loop_broke = True;
					break;

			# Only proceed if there was a non-whitespace character afterwards
			# i.e. the loop broke
			#if loop_broke == False: break; # (currently has issues)

			# Insert at index the new point - number and the author, and a newline
			sidebar_contents = (
				sidebar_contents[:index] +
				'* ' +
				'[{:,}](https://www.reddit.com/live/{}/updates/{})'
					.format(int(num), live.thread, data['id'])+
				' - /u/' +data['author']+ '\n'+
				sidebar_contents[index:]
			);
			
			# Update the sidebar with Reddit API
			response = live.reddit.request(
				method = 'POST',
				path = 'api/live/' +live.thread+ '/edit',
				data = {
					'api_type': 'json',
					'description': thread_info['description'],
					'nsfw': thread_info['nsfw'],
					'resources': sidebar_contents,
					'title': thread_info['title']
				}
			);


			break;

