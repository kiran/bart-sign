import requests
import os
import untangle
import time
from led_sign.client import SignClient

def get_bart_estimates(station='ROCK', direction=None):
  API_URL = 'http://api.bart.gov/api/etd.aspx'

  data = {
    'cmd': 'etd',
    'key': os.environ['BART_KEY'],
    'orig': station,
    'dir': direction,
  }

  r = requests.get(API_URL, params=data)
  doc = untangle.parse(r.text)

  lines = []

  # for each estimated destination,
  for etd in doc.root.station.etd:
    destination = etd.destination.cdata
    mins = []
    cars = None
    for estimate in etd.estimate:
      mins.append(estimate.minutes.cdata)
      cars = estimate.length.cdata
    lines.append(format_estimate(destination, cars, mins))

  return lines

def format_estimate(destination, cars, mins):
  minutes = ', '.join(mins)
  first_line = '{}: {} car train'.format(destination, cars)
  second_line = '{} mins'.format(minutes)
  return [first_line, second_line]

def main():
  # New client to write to led sign
  pwd = os.path.dirname(os.path.realpath(__file__))
  led_sign_path = '/'.join([pwd, 'led_sign']) 
  glyphs_path = '/'.join([led_sign_path, 'glyphs'])

  sign_client = SignClient(glyphs_path, led_sign_path)

  while True:
    estimates = get_bart_estimates('ROCK', 's')
    for est in estimates:
      sign_client.send_text_to_sign(est)
      time.sleep(3)
#-------------------------------------------------------------------------------
if __name__ == "__main__":
  main()
