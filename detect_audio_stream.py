import json
import requests
import subprocess
import time

# Script is paired with use of https://github.com/FDH2/UxPlay for handling AirPlay
# audio streaming. The purpose is to wait for audio playback to be detected and turn 
# on Zone 2 on my receiver thus allowing the played audio to make it to the speakers
# on my back porch. Once audio has stopped playing and the AirPlay device has 
# disconnected, Zone 2 on the receiver is powered off.

# This is intended to be run on a macOS machine, but could be adapted to Linux 
# easily enough...

# Send request to Home Assistant via the REST API
def ha_request(ha_path, entity_id, action):
  ha_url = 'http://homeassistant.local:8123'
  headers = {
    'Content-Type': 'application/json',
    # Token obscured
    'Authorization': 'Bearer XXXXXXXXXX'
  }
  data = {
    'entity_id': entity_id
  }
  api_response = None
  match str(action).lower():
    case 'get':
      try:
        api_response = requests.get(url=(ha_url + ha_path), headers=headers)
        print(f'Calling GET {ha_url + ha_path} - {api_response.status_code}')
      except Exception as e:
        print(f'Calling GET {ha_url + ha_path} - EXCEPTION')
        return None
    case 'post':
      try:
        api_response = requests.post(url=(ha_url + ha_path), headers=headers, json=data)
        print(f'Calling POST {ha_url + ha_path} - {api_response.status_code}')
      except Exception as e:
        print(f'Calling POST {ha_url + ha_path} - EXCEPTION')
        return None
      
  return api_response

# Use ha_request to get the power on state of Zone 2
def get_power_state(entity_id):
  ha_path = f'/api/states/{entity_id}'
  power_state = None
  api_response = ha_request(ha_path, entity_id, 'get')
  if api_response is not None:
    json_response: dict = json.loads(api_response.content)
    if 'state' in json_response.keys():
      power_state = json_response['state']
  print (f'Power is currently {power_state}')
  return power_state

# Use ha_request turn on/off Zone 2
def set_power_state(entity_id, state):
  ha_path = f'/api/services/media_player/turn_{str(state).lower()}'
  power_state = None
  api_response = ha_request(ha_path, entity_id, 'post')
  if api_response is not None:
    json_response: dict = json.loads(api_response.content)
    for response in json_response:
      if 'state' in response.keys():
        power_state = response['state']
  print (f'Power is now {power_state}')
  return power_state

# Found this mechanism for detecting audio playing via stackexchange, but not 
# really. It's just detecting if sleep is blocking by playing audio via coreaudiod 
# being the blocker. In my case, audio doesn't stop "playing" until audio stops and 
# the remote device disconnects from the AirPlay server, but that's good enough...
# https://apple.stackexchange.com/questions/363416/how-to-check-if-any-audio-is-currently-playing-via-terminal
def audio_playing():
  sleep_response = subprocess.run('pmset -g | grep " sleep"', shell=True, capture_output=True)
  if 'coreaudiod' in str(sleep_response.stdout):
    return True
  else:
    return False

entity_id = 'media_player.yamaha_receiver_back_porch'
power_state = get_power_state(entity_id)
previous_audio = audio_playing()
while True:
  api_response = None
  audio = audio_playing()
  if audio and audio != previous_audio:
    print('audio is playing')
    if str(power_state).lower() != 'on':
      power_state = set_power_state(entity_id, 'on')
  elif not audio and audio != previous_audio:
    print('audio is NOT playing')
    if str(power_state).lower() != 'off':
      power_state = set_power_state(entity_id, 'off')
  time.sleep(5)
  previous_audio = audio