from __future__ import print_function


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': None,
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def build_audio_response(output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': output
        },
        'card': None,
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
    speech_output = "Welcome to the Alexa Dracarys times skill. " \
                    "Think of me as a personal hype man for various sound effects."
    reprompt_text = "Please be a good hype man and give me something to do, for example say Let Me Hear It"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        speech_output, reprompt_text, should_end_session))
        
def play_sound_byte(intent, session):
    """plays sound byte at given url"""
    audio_output = '<speak><audio src="https://s3-us-west-2.amazonaws.com/gunny-alexa-sounds/dracarys_fixed.mp3" /></speak>'
    should_end_session = True

    return build_response({}, build_audio_response(
        audio_output, None, should_end_session))

def handle_session_end_request():
    speech_output = "I got you."
    should_end_session = True

    return build_response({}, build_speechlet_response(
        speech_output, None, should_end_session))

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
    if intent_name == "Play":
        return play_sound_byte(intent, session)
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
    

