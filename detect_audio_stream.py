import json
import logging
import os
import psutil  # for network interface names
import re
import requests
import socket
import subprocess
import time
from home_assistant import (get_power_state, set_power_state)
from process_info import collect_process_hosts

# Script is paired with use of https://github.com/FDH2/UxPlay for handling AirPlay
# audio streaming. The purpose is to wait for audio playback to be detected and turn 
# on Zone 2 on my receiver thus allowing the played audio to make it to the speakers
# on my back porch. Once audio has stopped playing and the AirPlay device has 
# disconnected, Zone 2 on the receiver is powered off.

# This is intended to be run on a macOS machine, but could be adapted to Linux 
# easily enough...

logger = logging.getLogger(__name__)

def audio_playing(clients):
    return True if clients else False

def main():
	logging.basicConfig(
		format='%(asctime)s %(levelname)-8s %(message)s',
		level=logging.INFO, 
		datefmt='%Y-%m-%d %H:%M:%S')
	entity_id = os.getenv("HASS_ENTITY")
	power_state = get_power_state(entity_id, logger)
	if str(power_state).lower() == 'on':
		logger.info(f'Power is already on for {entity_id}')
	clients = collect_process_hosts("uxplay", resolve_hostnames=True)
	previous_audio = audio_playing(clients)
	while True:
		api_response = None
		power_state = get_power_state(entity_id, logger)
		clients = collect_process_hosts("uxplay", resolve_hostnames=True)
		audio = audio_playing(clients)
		if audio and audio != previous_audio:
			if str(power_state).lower() != 'on':
				power_state = set_power_state(entity_id, 'on', (','.join(clients)), logger)
		elif not audio and audio != previous_audio:
			if str(power_state).lower() != 'off':
				power_state = set_power_state(entity_id, 'off', (','.join(clients)), logger)
		previous_audio = audio

if __name__ == "__main__":
	main()