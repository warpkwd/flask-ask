# -*- coding:utf-8 -*-

import logging
import os

from flask import Flask, json, Blueprint, render_template
from flask_ask import Ask, request, session, question, statement

hyakucnt = Blueprint('hyakucnt', __name__, url_prefix="/hyakucnt", static_folder='./hyakucnt')
ask = Ask(blueprint=hyakucnt)

logging.getLogger('flask_ask').setLevel(logging.DEBUG)

@ask.launch
def launch():
    card_title = render_template('card_title')
    question_text = render_template('welcome')
    reprompt_text = render_template('welcome_reprompt')
    return question(question_text).reprompt(reprompt_text).simple_card('card_title', reprompt_text)


@ask.intent('AnyCountIntent', convert={'from_': int, 'end': int})
def any_count(from_, end):
    if end > 100:
        end = 100
    if from_ < 1:
        from_ = 1
    
    if from_ == end:
        return cannot()
    if from_ > end:
        nums = list(range(from_, end - 1,  -1))
        msg = ', '.join([str(n) for n in nums])
        msg = '<speak>' + msg + '<break time="2s"/>  続けますか？</speak>'
        return question(msg).simple_card('%d から %d まで数えます' % (from_, end))

    if from_ < end:
        nums = list(range(from_, end + 1))
        msg = ', '.join([str(n) for n in nums])
        msg = '<speak>' + msg + '<break time="2s"/>  続けますか？</speak>'
        return question(msg).simple_card('%d から %d まで数えます' % (from_, end))


def cannot():
    return statement(msg).simple_card('数えられません')


@ask.intent('YesIntent')
def start():
    nums = list(range(1, 101))
    msg = ', '.join([str(n) for n in nums])
    msg = '<speak>' + msg + '<break time="2s"/>  続けますか？</speak>'
    return question(msg).simple_card('100 数えます')


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
#    app.run(debug=True,port=3001)

