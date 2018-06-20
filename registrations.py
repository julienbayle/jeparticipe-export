#!/usr/bin/env python3.6

import optparse
import csv
import json
import requests

def getActivitiesFromUrl(url):
	config_response = requests.get(url + '/config')

	if config_response.status_code != 200:
		raise Exception('Unable to get config')

	config = json.loads(config_response.text.encode('UTF-8'))
	return getActivitiesFromNode(config['blocs'])

def getActivitiesFromNode(entries, group_title = ''):
	activities = []

	group_title_pre = group_title
	if group_title_pre:
		group_title_pre += ' / '
	
	for entry in entries:
		if entry['type'] == 'group':
			activities += getActivitiesFromNode(entry['blocs'], group_title_pre + entry['title'])

		if entry['type'] == 'activity': 
			activities += [{
				'code': entry['code'],
				'group_title': group_title,
				'title': entry['title']
			}]

	return activities

def getRegistrations(url, code):
	registrations = []
	activity_response = requests.get(url + '/activity/' + code)

	if activity_response.status_code != 200:
		raise Exception("Unable to get activity {0}", code)

	activity_json = json.loads(activity_response.text.encode('UTF-8'))
	for participant in activity_json['Participants']:
		registrations += [{
			'name': participant['text'],
			'createdAt' : participant['createdAt']
		}]
	
	return registrations

def export(options):
	activities = getActivitiesFromUrl(options.url)
	success_count = 0
	error_count = 0

	with open(options.outputfile, 'w') as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames=['code', 'group_title', 'title', 'name', 'date'], delimiter=';', quotechar='"')
		writer.writeheader()

		for activity in activities :
			registrations = getRegistrations(options.url, activity['code'])
			for registration in registrations:
				activity["name"] = registration['name']
				activity["date"] = registration['createdAt']
				try :
					print(activity)
					writer.writerow(activity)
					success_count += 1
				except Exception as e:
					print(e)
					error_count += 1

	print("Exported to {0} with {1} success and {2} error(s)".format(options.outputfile, success_count, error_count))


if __name__ == "__main__":
	parser = optparse.OptionParser()
	parser.add_option('--url', action="store", dest='url', default="https://www.circuleo.fr/api/event/test", help="API URL (exemple : https://www.circuleo.fr/api/event/test)")
	parser.add_option('--output', action="store", dest='outputfile', default="export.csv", help="CSV output filename ")
	options, _ = parser.parse_args()
	export(options)
