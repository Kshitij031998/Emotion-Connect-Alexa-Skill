from connection import connect_peope_food
from connection import connect_peope_place

def food_connect(session):
    session_attributes = {}
    output= connect_peope_food(session)
    card_title = output

    reprompt_text = output
    speech_output= output
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, False))
        
def place_connect(session):
    session_attributes = {}
    output= connect_peope_place(session)
    card_title = output

    reprompt_text = output
    speech_output= output
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, False))
        
def on_intent(intent_request, session):
    if intent_name == "PlaceConnect":
        return place_connect(session)
    elif intent_name == 'FoodConnect':
        return food_connect(session)
