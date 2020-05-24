import mido
import time
import urllib.request
from threading import Timer

ports = mido.get_output_names()
url_base = 'http://192.168.10.1/api/control?alert='
url_val = ['000000','001000','010000','011000','100000','101000','110000','111000']
note_idx = [0,50,52,55,57,59,60,62]
watchdog_time = 0.1
elapsed_time = 0

class Watchdog:
  def __init__(self, timeout, userHandler=None):
    self.timeout = timeout
    self.handler = userHandler if userHandler is not None else self.defaultHandler
    self.timer = Timer(self.timeout, self.handler)
    self.timer.start()

  def reset(self):
    self.timer.cancel()
    self.timer = Timer(self.timeout, self.handler)
    self.timer.start()

  def stop(self):
    self.timer.cancel()

  def defaultHandler(self):
    raise self

def myHandler():
  global watchdog
  url = url_base + url_val[0]
  print(url) # Debug Code
  req = urllib.request.urlopen(url)
  watchdog.stop()

watchdog = Watchdog(watchdog_time, myHandler)
watchdog.stop()

with mido.open_output(ports[0]) as outport:
  for msg in mido.MidiFile('DanceOnTheInside.mid'):
    sleep_time = msg.time - elapsed_time
    if sleep_time <0:
      msg.time = msg.time + sleep_time
      elapsed_time = abs(sleep_time)
      sleep_time = 0
    else:
      elapsed_time = 0

    time.sleep(sleep_time)
    if not msg.is_meta:
      if(str(msg.type)=="note_on"):
        if(msg.velocity == 0):
          watchdog.reset()
        else:
          index = note_idx.index(msg.note)
          url = url_base + url_val[index]
          print(url) # Debug Code

          start = time.time()
          req = urllib.request.urlopen(url)
          elapsed_time = elapsed_time + time.time() - start
          watchdog.stop()

      outport.send(msg) 
