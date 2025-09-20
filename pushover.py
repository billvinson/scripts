import os
import requests

def pushover_message(message: str, device: str = None, attachment_filename: str = None):
  if not message:
    return

  token = os.getenv("PUSHOVER_TOKEN")
  user = os.getenv("PUSHOVER_USER")

  if any(v is None for v in [token, user]):
    return

  request_body = {
    "token": token,
    "user": user,
    "message": message
  }

  if device:
    request_body['device'] = device

  if attachment_filename:
    r = requests.post(
      "https://api.pushover.net/1/messages.json", 
      data = request_body, 
      files = {"attachment": ("image.jpg", open(attachment_filename, "rb"), "image/jpeg")}
    )
  else:
    r = requests.post("https://api.pushover.net/1/messages.json", data = request_body)
