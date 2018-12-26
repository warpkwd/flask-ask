# -*- coding:utf-8 -*-

import logging
import os

from flask import Flask, json, Blueprint, render_template
from flask_ask import Ask, request, session, question, statement, audio

todaykoh = Blueprint('todaykoh', __name__, url_prefix="/todaykoh", static_folder='./todaykoh')
## print (__name__)  // todaykoh.session
ask = Ask(blueprint=todaykoh)

log = logging.getLogger()
logging.getLogger('flask_ask').setLevel(logging.DEBUG)

end = 8
level = int (end/2)


@ask.launch
def launch():
    card_title = render_template('card_title')
    msg = "today card_title:%s" % card_title
    print(msg)
    question_text = render_template('welcome')
    msg = "today question_text:%s" % question_text
    print(msg)
    question_text_card = render_template('welcome_card')
    reprompt_text = render_template('welcome_reprompt')
    session.attributes['question_number'] = 0
    session.attributes['yes_count'] = 0
    return question(question_text).reprompt(reprompt_text).simple_card(card_title, question_text_card)

@ask.intent("YesIntent")
def today_good():
    res = session.attributes['yes_count']
    num = session.attributes['question_number']
    res = res + 1
    session.attributes['yes_count'] = res
    num = num + 1
    if num > end:
        return finished(res)
    q_num = 'q_%s' % num
    session.attributes['question_number'] = num
    card_title = render_template('card_title')
    val = render_template('good')
    question_ssml = '<speak>' + val + '<break time="1s"/>' + render_template(q_num) + '</speak>'
    question_text = val + '  ' + render_template(q_num)
    reprompt_text = render_template(q_num)
    return question(question_ssml).reprompt(reprompt_text).simple_card(card_title, question_text)

@ask.intent("NoIntent")
def today_ng():
    res = session.attributes['yes_count']
    num = session.attributes['question_number']
    session.attributes['yes_count'] = res
    num = num + 1
    if num > end:
        return finished(res)
    q_num = 'q_%s' % num
    session.attributes['question_number'] = num
    card_title = render_template('card_title')
    val = render_template('bad')
    question_ssml = '<speak>' + val + '<break time="1s"/>' + render_template(q_num) + '</speak>'
    question_text = val + render_template(q_num)
    reprompt_text = render_template(q_num)
    return question(question_ssml).reprompt(reprompt_text).simple_card(card_title, question_text)

def finished(res):
    val = 'win'
    if res < level:
        val = 'lose'

    question_text = '<speak>' + render_template(val) + '<break time="1s"/>' + render_template('bye') + '</speak>'
    card_title = render_template('card_title')
#    return statement(question_text).simple_card(card_title, question_text)
    stream_url = 'https://api.foobar.net/page/correct1.mp3'
    return audio(question_text).play(stream_url).simple_card(card_title, question_text)

@ask.intent('AMAZON.StopIntent')
def stop():
    bye_text = render_template('bye')
    return statement(bye_text)

@ask.intent('AMAZON.CancelIntent')
def cancel():
    bye_text = render_template('bye')
    return statement(bye_text)

@ask.session_ended
def session_ended():
    return "{}", 200


#if __name__ == '__main__':
#    if 'ASK_VERIFY_REQUESTS' in os.environ:
#        verify = str(os.environ.get('ASK_VERIFY_REQUESTS', '')).lower()
#        if verify == 'false':
#            app.config['ASK_VERIFY_REQUESTS'] = False
#    app.run(debug=True,port=3000)
