import json
import os
import requests
from pushover import pushover_message

# Send request to Home Assistant via the REST API
def ha_request(ha_path, entity_id, action, logger = None):
    if logger is None:
        logger = logging.getLogger(__name__)

    token = os.getenv("HASS_TOKEN")
    if token is None:
        logger.info('Token missing - skipping Home Assistant request')
        return None

    if entity_id is None:
        logger.info('HA entity id missing - skipping Home Assistant request')
        return None

    ha_url = 'http://homeassistant.local:8123'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    data = {
        'entity_id': entity_id
    }
    api_response = None
    match str(action).lower():
        case 'get':
            try:
                api_response = requests.get(url=(ha_url + ha_path), headers=headers)
                # logger.info(f'Calling GET {ha_url + ha_path} - {api_response.status_code}')
            except Exception as e:
                logger.info(f'Calling GET {ha_url + ha_path} - EXCEPTION')
                return None
        case 'post':
            try:
                api_response = requests.post(url=(ha_url + ha_path), headers=headers, json=data)
                # logger.info(f'Calling POST {ha_url + ha_path} - {api_response.status_code}')
            except Exception as e:
                logger.info(f'Calling POST {ha_url + ha_path} - EXCEPTION')
                return None
      
    return api_response

# Uses ha_request to get the power on state of the entity
def get_power_state(entity_id, logger = None):
    ha_path = f'/api/states/{entity_id}'
    power_state = None
    api_response = ha_request(ha_path, entity_id, 'get', logger)
    if api_response is not None:
        json_response: dict = json.loads(api_response.content)
        if 'state' in json_response.keys():
            power_state = json_response['state']
    return power_state

# Uses ha_request turn on/off the entity
def set_power_state(entity_id, state, client, logger = None):
    ha_path = f'/api/services/media_player/turn_{str(state).lower()}'
    power_state = None
    api_response = ha_request(ha_path, entity_id, 'post', logger)
    if api_response is not None:
        json_response: dict = json.loads(api_response.content)
        for response in json_response:
            if 'state' in response.keys():
                power_state = response['state']
                logger.info(f'Power is now {power_state}{f" via {client}" if client else ''}')
                pushover_message(f'Power to back porch is now {power_state}{f" via {client}" if client else ''}')
            if not power_state:
                logger.info(response)
    return power_state