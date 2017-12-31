# look for youtube URLs in IRC buffers, print info (title, channel) in the relevant buffers.

# Most lines taken from https://github.com/snowfag/weechat-scripts/blob/master/youtube.py

import requests
import weechat as wc
import re

name = 'youtube.py'
wc.register(name, 'Barnaba Turek', '0.1', 'BSD-2c', 'Youtube video title announcer', '', '')

def config(*args, **kwargs):
  global channels, api_key, bots_list
  if not wc.config_is_set_plugin('api_key'):
      wc.config_set_plugin('api_key', 'not_set')
  api_key = wc.config_get_plugin('api_key')
  if re.match('^\${sec\.data\.(.*)}$', api_key):
      api_key = wc.string_eval_expression(api_key, {}, {}, {})
  return wc.WEECHAT_RC_OK

def privmsg(data, signal, signal_data):
  (server, signal) = signal.split(',')
  details = wc.info_get_hashtable('irc_message_parse', {'message': signal_data, 'server': server})
  buffer_name = details['channel'].lower()
  buffer_pointer = wc.info_get('irc_buffer', '{},{}'.format(server, buffer_name))
  if not api_key == 'not_set':
    youtube_regex_match = re.compile(r'(.*https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([a-zA-Z0-9_-]{11})').match(details['text'])
    if youtube_regex_match:
      vid_id = youtube_regex_match.group(6)
      rvt = requests.get('https://www.googleapis.com/youtube/v3/videos/?id={}&part=snippet&key={}'.format(vid_id, api_key))
      try:
	vid_title = rvt.json()['items'][0]['snippet']['title'].encode('utf-8')
	vid_channel = rvt.json()['items'][0]['snippet']['channelTitle'].encode('utf-8')
	wc.prnt(buffer_pointer, r'[Youtube] {} @ Channel: {}'.format(vid_title, vid_channel))
      except:
	wc.prnt(buffer_pointer, '[Youtube] Error getting video info.')
  else:
    wc.prnt(buffer_pointer, r'[Youtube] Set your API key at plugins.var.python.{}.api_key'.format(name))
  return wc.WEECHAT_RC_OK

wc.hook_config('plugins.var.python.' + name + '.*', 'config', '')
wc.hook_signal('*,irc_in_privmsg', 'privmsg', '')
config()
