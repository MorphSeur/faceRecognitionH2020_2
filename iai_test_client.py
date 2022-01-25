# -*- coding: utf-8 -*-
import os
import requests
from argparse import ArgumentParser
from flask import Flask, jsonify, request

cback_app = Flask(__name__)

@cback_app.route('/callback')
def callback():
  print("Callback received!!!")

def send_start(args):
  url = "{}/startAnalytics".format(args.target)
  """
      ar.session_id = payload['session_id']
      ar.iai_datalake = payload['iai_datalake']
      # Data cipher used to decrypt data or None when no encryption
      ar.iai_datacipher = payload['iai_datacipher']
      ar.iai_datakey = payload['iai_datakey']
      ar.iai_params = getattr(payload, 'iai_params', None)
      ar.iai_files = payload['iai_files']
      ar.on_finish_url = payload['on_finish_url']
  """
  payload = dict(
    session_id=args.session_id,
    iai_datalake=args.datalake,
    iai_datacipher=None,
    iai_datakey=None,
    iai_files=args.files,
    on_finish_url=None)

  ret = requests.post(url, json=payload)
  print("Server response: [status={}, body={}]".format(ret.status_code, ret.json() if ret.status_code == 200 else ret.content.decode('UTF-8')))

def send_stop(args):
  url = "{}/stopAnalytics".format(args.target)

  ret = requests.put(url, params={'session_id': args.session_id})
  print("Server response: [status={}, body={}]".format(ret.status_code, ret.json() if ret.status_code == 200 else ret.content.decode('UTF-8')))


def main():
  p = ArgumentParser()
  p.add_argument('--target', '-t', default='http://localhost:5000', help="Address where iai agent server is running")
  subparsers = p.add_subparsers(help='Available action', dest='action')
  p_start = subparsers.add_parser('start')
  p_start.add_argument('--datalake', '-dl', required=True)
  p_start.add_argument('--session-id', default='1234')
  p_start.add_argument('files', nargs='+')

  p_stop = subparsers.add_parser('stop')
  p_stop.add_argument('--session-id', default='1234')

  args = p.parse_args()
  print(args)

  if args.action == 'start':
    send_start(args)
  elif args.action == 'stop':
    send_stop(args)


if __name__ == '__main__':
  main()
