# -*- coding: utf-8 -*-
from collections import UserDict
from multiprocessing import Process
from threading import Thread
import os
import requests
import logging


Log = logging.getLogger('server.iai')

def set_logger(logger):
  Log = logger

class _AnalyticsPool(UserDict):
  _instance = None

  def add(self, instance):
    session_id = instance.get_session_id()
    Log.debug('Add worker with session_id=%s', session_id)
    self.data[session_id] = instance

  def get(self, session_id):
    return self.data[session_id]

  def remove(self, session_id):
    Log.debug('Remove worker with session_id=%s', session_id)
    self.data.pop(session_id)

  def instance():
    if _AnalyticsPool._instance is None:
      _AnalyticsPool._instance = _AnalyticsPool()

    return _AnalyticsPool._instance

def get_analytics_pool():
  return _AnalyticsPool.instance()

class AnalyticsRequest(object):
  session_id = None
  iai_datalake = None
  iai_datacipher = None
  iai_datakey = None
  iai_params = None
  iai_files = []
  on_finish_url = None

  SCHEMA = {
    "type": "object",
    "properties": {
      "session_id": {"type": "string"},
      "iai_datalake": {"type": "string"},
      "iai_datacipher": {"type": ["string", "null"]},
      "iai_datakey": {"type": ["string", "null"]},
      "iai_files": {"type": "array", "items": {"type": "string"}},
      "iai_params": {"type": ["object", "null"]},
      "on_finish_url": {"type": ["string", "null"]},
    },
    "required": [ "session_id", "iai_datalake", "iai_datacipher", "iai_datakey",
                  "iai_files", "on_finish_url"]
  }

  def from_params(payload):
    ar = AnalyticsRequest()

    ar.session_id = payload['session_id']
    ar.iai_datalake = payload['iai_datalake']
    # Data cipher used to decrypt data or None when no encryption
    ar.iai_datacipher = payload['iai_datacipher']
    ar.iai_datakey = payload['iai_datakey']
    ar.iai_files = payload['iai_files']
    ar.iai_params = getattr(payload, 'iai_params', None)
    ar.on_finish_url = payload['on_finish_url']

    return ar

  def __str__(self):
    attributes = " ".join(["{}={}".format(k, getattr(self, k)) for k in self.__dict__])
    return "<AnalyticsRequest {}>".format(attributes)


class AnalyticsAgent(object):
  def __init__(self, params):
    self.params = params
    self.p = None

  def get_session_id(self):
    return self.params.session_id

  def start(self):
    self.p = p = Process(target=self.run)
    p.daemon = True
    return p.start()

  def terminate(self):
    # Handle real terminate in separate thread in order to not block server
    # request
    Thread(target = self._terminate_thread).start()

  def _terminate_thread(self):
    try:
      # Tell analytics to terminate
      self.end()
    finally:
      self.p.terminate()

  def on_finish(self, success, value, resuls):
    payload = {
      'success': success,
      'value': value,
      'resuls': resuls
    }
    if not self.params.on_finish_url:
      Log.error('[WARNING] No on_finish_url provided in request (payload={})'.format(payload))
    else:
      requests.post(self.params.on_finish_url, payload)

  def run(self):
    raise NotImplementedError("Call abstract method run()")

  def end(self):
    raise NotImplementedError("Call abstract method end()")

  def build_datalake_path(self, *args):
    return os.path.join(self.params.iai_datalake, *args)

  def read_input(self, dpoid):
    """
    Read dpo from datalake and perform decrypt using the information provided
    by IAI
    """

    path = self.build_datalake_path(dpoid)
    if not self.params.iai_datacipher:
      with open(path, 'rb') as f:
        return f.read()

    raise NotImplementedError("Reading crypted files is not implemented yet")


  def write_output(self, name, plaintext_content):
    """
    Write new file in datalake and encrypt the contents using the information
    provided by IAI
    """
    filepath = self.build_datalake_path(name)
    if not self.params.iai_datacipher:
      with open(filepath, 'wb') as f:
        f.write(plaintext_content)
      return

    raise NotImplementedError("Writing crypted files is not implemented yet")

