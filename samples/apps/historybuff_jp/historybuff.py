# -*- coding: utf-8 -*-

import logging
import os
import re
import datetime,pytz
from six.moves.urllib.request import urlopen
import urllib
import chardet

from flask import Flask, Blueprint
from flask_ask import Ask, request, session, question, statement


historybuff = Blueprint('historybuff', __name__, url_prefix="/historybuff", static_folder='./historybuff_jp')
ask = Ask(blueprint=historybuff)

logging.getLogger('flask_ask').setLevel(logging.DEBUG)


# URL prefix to download history content from Wikipedia.
URL_PREFIX = 'https://ja.wikipedia.org/w/api.php?action=query&prop=extracts' + \
    '&format=json&explaintext=&exsectionformat=plain&redirects=&titles='

# Constant defining number of events to be read at one time.
PAGINATION_SIZE = 3

# Length of the delimiter between individual events.
DELIMITER_SIZE = 2

# Size of events from Wikipedia response.
# SIZE_OF_EVENTS = 10
SIZE_OF_EVENTS = 11

# Constant defining session attribute key for the event index
SESSION_INDEX = 'index'

# Constant defining session attribute key for the event text key for date of events.
SESSION_TEXT = 'text'


LOG_FILENAME = './mylogger.log'
def my_logger(msg):         # Y.Kawada
    return
    """write file directly"""
    str = "%s: %s\n" % (datetime.datetime.now(), msg)
    f = open(LOG_FILENAME, 'a')
    try:
        f.write(str)
    finally:
        f.close()

@ask.launch
def launch():
    speech_output = 'ヒストリーバフ。 何のイベントの日付が知りたいですか？'
    reprompt_text = "ヒストリーバフでは、あなたは年の任意の日の歴史的なイベントを得ることができます。 " + \
                    "たとえば、今日、または8月30日と言うことができます。 " + \
                    "今、あなたはいつが知りたいですか？"
    return question(speech_output).reprompt(reprompt_text)


@ask.intent('GetFirstEventIntent', convert={ 'day': 'date' })
def get_first_event(day):
    my_logger("day:%s" % day)
    month_name = day.strftime('%-m')
    day_number = day.day
    events = _get_json_events_from_wikipedia(month_name, day_number)
    my_logger("events:%s" % events)
    if not events:
        speech_output = "現時点では Wikipedia への接続に問題があります。 後でもう一度お試しください。"
        return statement('<speak>{}</speak>'.format(speech_output))
    else:
        card_title = "{}月{}日 のイベント".format(month_name, day_number)
        speech_output = "<p>{}月{}日 のイベント</p>".format(month_name, day_number)
        card_output = ""
        for i in range(PAGINATION_SIZE):
            speech_output += "<p>{}</p>".format(events[i].encode('ascii').decode('unicode-escape'))
            card_output += "{}\n".format(events[i].encode('ascii').decode('unicode-escape'))
        speech_output += " 歴史をもっと深く知りたいですか？"
        card_output += " 歴史をもっと深く知りたいですか？"
        reprompt_text = "ヒストリーバフでは、あなたは年の任意の日の歴史的なイベントを得ることができます。 " + \
                    "たとえば、今日、または8月30日と言うことができます。 " + \
                    "今、あなたはいつが知りたいですか？"
        session.attributes[SESSION_INDEX] = PAGINATION_SIZE
        session.attributes[SESSION_TEXT] = events
        speech_output = '<speak>{}</speak>'.format(speech_output)
        return question(speech_output).reprompt(reprompt_text).simple_card(card_title, card_output)


@ask.intent('GetNextEventIntent')
def get_next_event():
    events = session.attributes[SESSION_TEXT]
    index = session.attributes[SESSION_INDEX]
    card_title = "歴史の中のこの日のより多くの出来事"
    speech_output = ""
    card_output = ""
    i = 0
    while i < PAGINATION_SIZE and index < len(events):
        speech_output += "<p>{}</p>".format(events[index].encode('ascii').decode('unicode-escape'))
        card_output += "{}\n".format(events[index].encode('ascii').decode('unicode-escape'))
        i += 1
        index += 1
    speech_output += " 歴史をもっと深く知りたいですか？"
    reprompt_text = "この日に何が起こったのかを知りたいですか？"
    session.attributes[SESSION_INDEX] = index
    speech_output = '<speak>{}</speak>'.format(speech_output)
    return question(speech_output).reprompt(reprompt_text).simple_card(card_title, card_output)


@ask.intent('AMAZON.StopIntent')
def stop():
    return statement("さようなら")


@ask.intent('AMAZON.CancelIntent')
def cancel():
    return statement("さようなら")


@ask.session_ended
def session_ended():
    return "{}", 200


def _get_json_events_from_wikipedia(month, date):
    dt = "{}月{}日".format(month, date)
    dtt = urllib.parse.quote(dt)
    url= "{}{}".format(URL_PREFIX, dtt)
    my_logger("url:%s" % url)

    req=urllib.request.urlopen(url)
    charset = req.info().get_content_charset()
    data = req.read().decode(charset)
    return _parse_json(data)


def _parse_json(text):
    events = []
    try:
#        slice_start = text.index("\\nEvents\\n") + SIZE_OF_EVENTS
#        slice_end = text.index("\\n\\n\\nBirths")
        _ev = 'できごと'.encode('unicode_escape')
        ev = _ev.decode('utf-8')
        my_logger("_ev:%s"  % ev)
        slice_start = text.find("\\n" + ev + "\\n") + SIZE_OF_EVENTS
        my_logger("start:%s"  % slice_start)
        _bt = '誕生日'.encode('unicode_escape')
        bt = _bt.decode('utf-8')
        my_logger("_bt:%s"  % bt)
        slice_end = text.find("\\n\\n\\n"+ bt)
        my_logger("end:%s"  % slice_end)
        text = text[slice_start:slice_end];
    except ValueError as e :
        my_logger("Exception error:%s" % e)
        return events
    start_index = end_index = 0
    done = False
    while not done:
        try:
            end_index = text.index('\\n', start_index + DELIMITER_SIZE)
            event_text = text[start_index:end_index]
            start_index = end_index + 2
        except ValueError:
            event_text = text[start_index:]
            done = True
        # replace dashes returned in text from Wikipedia's API
        event_text = event_text.replace('\\u2013', '')
        # add comma after year so Alexa pauses before continuing with the sentence
        event_text = re.sub('^\d+', r'\g<0>', event_text)
        events.append(event_text)
    events.reverse()
    return events


#if __name__ == '__main__':
#    if 'ASK_VERIFY_REQUESTS' in os.environ:
#        verify = str(os.environ.get('ASK_VERIFY_REQUESTS', '')).lower()
#        if verify == 'false':
#            app.config['ASK_VERIFY_REQUESTS'] = False
#    app.run(debug=True,port=3002)
