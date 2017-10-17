from __future__ import print_function

import urllib
import urllib2
import json

API_BASE = "https://min-api.cryptocompare.com/data/"

KNOWN_CURRENCIES = ['BTC', 'BCC', 'ETC', 'LTC', 'XMR']
SPELL_OUT = "<say-as interpret-as=\"spell-out\">%s</say-as>"
SAY_AS_NUMBER = "<say-as interpret-as=\"cardinal\">%d</say-as>"


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_intro():
    session_attributes = {}
    card_title = "CryptoButler"
    speech_output = "<speak>Welcome to the Alexa CryptoButler skill. What currency are you interested in?</speak>"
    reprompt_text = "<speak>Give me a currency to lookup, for example <say-as interpret-as=\"spell-out\">BTC</say-as></speak>"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def price_lookup(intent, session):
    """plays sound byte at given url"""
    session_attributes = {}
    card_title = "CryptoButler - Lookup"
    speech_output = "<speak>I'm not sure which currency you're looking for. " \
                    "Please try again.</speak>"
    reprompt_text = "<speak>I'm not sure which currency you're looking for. " \
                    "Try asking about <say-as interpret-as=\"spell-out\">BTC</say-as>.</speak>"
    should_end_session = False

    if "Currency" in intent["slots"]:
        currency_symbol = intent["slots"]["Currency"]["value"]

        if (currency_symbol in KNOWN_CURRENCIES):
            card_title = "CryptoButler PriceLookup " + currency_symbol
            request_data = {'fsym': currency_symbol.upper(), 'tsym': 'USD'}
            query_params = urllib.urlencode(request_data)

            response = urllib2.urlopen(API_BASE + "price?" + query_params)
            response_data = json.load(response)

            currency_value = float(response_data.get('USD'))

            speech_output = "<speak><say-as interpret-as=\"spell-out\">%s</say-as> is currently worth <say-as interpret-as=\"cardinal\">%d</say-as> US dollars</speak>" % (currency_symbol, currency_value)
            reprompt_text = ""

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "CryptoButler - Thanks"
    speech_output = "<speak>Good luck.</speak>"
    should_end_session = True

    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


# --------------- Events ------------------
def on_session_started(session_started_request, session):
    print("Starting new session.")


def on_launch(launch_request, session):
    return get_intro()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "PriceLookUp":
        return price_lookup(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_intro()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    print("Ending session.")


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    if (event['session']['application']['applicationId'] !=
            "amzn1.ask.skill.774b5d66-0b4f-49ed-9cc2-4dd5b9973b20"):
        raise ValueError("Invalid Application ID")

    if event["session"]["new"]:
        on_session_started({"requestId": event["request"]["requestId"]}, event["session"])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    if event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])