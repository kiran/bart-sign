import requests
import sys
import os
import untangle
import time
from led_sign.client import SignClient
from datetime import datetime
from pytz import timezone

def get_bart_estimates(station='ROCK', direction=None):
  API_URL = 'http://api.bart.gov/api/etd.aspx'

  try:
    key = os.environ['BART_KEY']
  except KeyError:
    print('Set the BART_KEY environment variable')
    raise

  data = {
    'cmd': 'etd',
    'key': key,
    'orig': station,
    'dir': direction,
  }
  
  r = requests.get(API_URL, params=data)

  if r.status_code != 200:
    print("returned {}".format(r.status_code))
    return [["error: {}".format(r.status_code),'']]

  doc = untangle.parse(r.text)

  lines = []

  # for each estimated destination,
  try:
    for etd in doc.root.station.etd:
      destination = etd.destination.cdata
      mins = []
      cars = None
      for estimate in etd.estimate:
        mins.append(estimate.minutes.cdata)
        cars = estimate.length.cdata
      lines.append(format_estimate(destination, cars, mins))
  except:
    print(r.text)
    print(sys.exc_info()[0])
    lines = [['No trains','until next morning']]
  lines.append(get_time_lines())
  return lines

def get_time_lines():
  pst = timezone('US/Pacific')
  pst_time = datetime.now(pst)
  return [pst_time.strftime('%b %d, %Y'), pst_time.strftime('%H:%M')]

def format_estimate(destination, cars, mins):
  minutes = ', '.join(mins)
  first_line = '{}'.format(destination, cars)
  second_line = '{} mins'.format(minutes)
  return [first_line, second_line]

def main():
  # New client to write to led sign
  pwd = os.path.dirname(os.path.realpath(__file__))
  led_sign_path = '/'.join([pwd, 'led_sign']) 
  glyphs_path = '/'.join([led_sign_path, 'glyphs'])

  sign_client = SignClient(glyphs_path, led_sign_path)

  while True:
    try:
      estimates = get_bart_estimates('ROCK', 's')
      sign_client.send_text_to_sign(estimates)
      time.sleep(30)
    except:
      sign_client.send_text_to_sign(['ERROR',''])
      print(sys.exc_info()[0])
      raise
      time.sleep(3)
#-------------------------------------------------------------------------------
if __name__ == "__main__":
  main()
