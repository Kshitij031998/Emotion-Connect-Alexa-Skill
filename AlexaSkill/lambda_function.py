from __future__ import print_function
import boto3
import requests
from boto3.dynamodb.conditions import Key, Attr
from connection import connect_peope_food
from connection import connect_peope_place,top_people


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
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

def get_sentiment(text):
    url="https://api.dandelion.eu/datatxt/sent/v1"
    token="8243df2b739e4df2a8c3cc0fd8afa415"
    response=requests.get(url=url,params={"text":text,"token":token,'lang':'en'})
    sentiment=response.json()['sentiment']['type']
    score=response.json()['sentiment']['score'] 
    return str(score)

def dump_data(table,user_id,entity_name,entity_type,sentiment):
    row = table.query(KeyConditionExpression=(Key('ID').eq(user_id) & Key('EntityName').eq(entity_name)))
    if(row['Count']==0):
        N=1 
    else:
        N=row['Items'][0]['N']
        sentiment=str((float(row['Items'][0]['Sentiment'])*float(N)+float(sentiment))/float((N+1)))
        N+=1
    
    table.put_item(
                    Item={
                    'ID': user_id,
                    'EntityType':entity_type,
                    'EntityName':entity_name.lower(),
                    'Sentiment':sentiment,
                    'N':N
                    })
    
    

# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response(user_id):
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
    table = dynamodb.Table('user_id_name')

    user = table.query(
        KeyConditionExpression=Key('ID').eq(user_id)
    )
    speech_output="hello"
    if (user['Count'] == 0):
       
        speech_output = "Hello.!"\
                        "Welcome to My Emotion. "\
                        " My emotion is an advanced Daily Logger which helps you to understand more "\
                        "about yourself and to connect with people of similar interests."\
                        " You can share your day by saying , I would like to share my day."\
                        " You can connect with people of similar interests by saying, "\
                        " Connect with someone who likes the same food as me,"\
                        " or, Connect with someone who likes the same place as me."\
                        " You can get to know more about yourself by saying,"\
                       " What food do i like the most , or , Which place do I like the most , or, "\
                        " Whom do i like the most."\
                        " You can turn of contact sharing by saying, remove my phone number."\
                        " At any point of conversation you can say Bye Emotion to end the conversation. ThankYou. "\
                        "You seem to be new, May I know your name? For example ,You can say, My name is Daniel or I am Daniel. "
        reprompt_text=speech_output
    else:
        speech_output = 'Hey ' + user['Items'][0]['Name'] + ", Welcome to My Emotion App! " \
                                                           "Would you like to share your day ,or , would you like to get some suggestions? You can end this conversation by saying, Bye emotion?"
        reprompt_text=speech_output

    session_attributes = {}
    card_title = "Welcome to My Emotion"


    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
        
        
    
def build_response7(message, session_attributes={}):
    response = {}
    response['version'] = '1.0'
    response['sessionAttributes'] = session_attributes
    response['response'] = message
    return response

def continue_dialog5(intent):
    message = {}
    message['shouldEndSession'] = False
    message['directives'] = [{'type': 'Dialog.Delegate','updatedIntent':intent}]
    return build_response7(message)


def set_name(intent, session,dialog_state):
    
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
    table = dynamodb.Table('user_id_name')

    user_id = session['user']['userId'].split('.')[3]
    user = table.query(KeyConditionExpression=Key('ID').eq(user_id))
    if (user['Count'] == 0):
        output="Awsome, Thanks for the infomation. Would you like to share your day or would you like to get some suggestions? You can end this conversation by saying, Bye emotion"
        card_title = "Thanks for the infomation."

        arr = [0] * 2
        slots = intent['slots']
        for i, slot in enumerate(slots):
            if 'value' in slots[slot]:
                arr[i] = 1
                
        is_it_over=intent['confirmationStatus']
        if 'value' in intent['slots']['PhoneNumber']:
            phone_number=intent['slots']['PhoneNumber']['value']
            phone_number=" ".join(phone_number)
            intent['slots']['PhoneNumber']['value']=phone_number
    
        if is_it_over =="NONE":
            if dialog_state in ("STARTED", "IN_PROGRESS"):
                return continue_dialog5(intent)
            elif dialog_state == "COMPLETED":
                return statement("trip_intent", "Have a good trip")
            else:
                return statement("trip_intent", "No dialog")
        else:
            can_share=True if is_it_over =="CONFIRMED" else False
            name = intent['slots']['name']['value']
            user_id = session['user']['userId'].split('.')[3]
            phoneNumber = intent['slots']['PhoneNumber']['value']
            phoneNumber="".join(["" if i ==" " else i for i in phoneNumber])
            dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
            table = dynamodb.Table('user_id_name')
            
            table.put_item(
                Item={
                    'ID': user_id,
                    'Name': name,
                    'PhNo':phoneNumber,
                    'CanShare':can_share
                })
    else:
        output="Your allready done with your registration. Would you like to share your day or would you like to get some suggestions? You can end this conversation by saying, Bye emotion"
        card_title = "How can I help you ?"

    speech_output=output
    session_attributes = {}

    reprompt_text = "I'm still waiting , Would you like to share your day or would you like to get some suggestions? You can end this conversation by saying, Bye emotion"

    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
            card_title, speech_output, reprompt_text, should_end_session))
        


def build_response2(message, session_attributes={}):
    response = {}
    response['version'] = '1.0'
    response['sessionAttributes'] = session_attributes
    response['response'] = message
    return response


def continue_dialog(intent, session,arr):
    import random
    message = {}
    if ((not arr[3]) & (not arr[4]) & (not arr[5])):
        dir = [{"type": "Dialog.ElicitSlot", "slotToElicit": "Food", "updatedIntent": intent}]
        all=["What special food did you have today. You can say skip if you had the same routine food.",
        "Did you try anything different today for filling your tummy. You can say skip if you had the same routine food."]
        out_speech = random.choice(all)

    elif ((not arr[0]) & (not arr[3]) & (not arr[4]) & (arr[5]) & (intent['slots']['Food']["value"] not in ['no','nothing','skip'])):
        dir = [{"type": "Dialog.ElicitSlot", "slotToElicit": "FoodExperience", "updatedIntent": intent}]
        food=intent['slots']['Food']["value"]
        all=['What did you feel about {} '.format(food), 'Was {} of any good'.format(food)]
        out_speech = random.choice(all)
 
    elif ((not arr[3]) & (not arr[4]) & (arr[5])):
        dir = [{"type": "Dialog.ElicitSlot", "slotToElicit": "Person", "updatedIntent": intent}]
        all=['Did you meet anyone special today. If yes May I know their name. You can say skip if you did not meet anyone special.','Did you get to know anyone today. If yes May I know their name .You can say skip if you did not meet anyone new.']
        out_speech = random.choice(all)

    elif ((not arr[1]) & (arr[3]) & (not arr[4]) & (arr[5]) & (intent['slots']['Person']["value"] not in ['no','no one','skip'])):
        dir = [{"type": "Dialog.ElicitSlot", "slotToElicit": "PersonExperience", "updatedIntent": intent}]
        person=intent['slots']['Person']["value"]
        all=['How was your meeting with {}'.format(person),'How did your meeting with {} go about'.format(person)]
        out_speech = random.choice(all)

    elif ((arr[3]) & (not arr[4]) & (arr[5])):
        dir = [{"type": "Dialog.ElicitSlot", "slotToElicit": "Place", "updatedIntent": intent}]
        all=['Did you go to any special place today? You can say skip if you did not go to any special place.','Did you visit any special place today? You can say skip if you did not visit any special place.']
        out_speech = random.choice(all)

    elif ((not arr[2]) & (arr[3]) & (arr[4]) & (arr[5]) & (intent['slots']['Place']["value"] not in ['no','no where','skip'])):
        dir = [{"type": "Dialog.ElicitSlot", "slotToElicit": "PlaceExperience", "updatedIntent": intent}]
        place=intent['slots']['Place']["value"]
        all=['Did you enjoy in {}?'.format(place),'How was {}'.format(place)]
        out_speech = random.choice(all)

    else:
        food=intent['slots']['FoodExperience']
        person=intent['slots']['PersonExperience']
        place=intent['slots']['PlaceExperience']
        user_id = session['user']['userId'].split('.')[3]
        
        dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
        table = dynamodb.Table('user_emotion')
        
        if 'value' in food:
            dump_data(table,user_id,intent['slots']['Food']['value'],'Food',get_sentiment(food['value']))
        if 'value' in person:
            dump_data(table,user_id,intent['slots']['Person']['value'],'Person',get_sentiment(person['value']))
        if 'value' in place:
            dump_data(table,user_id,intent['slots']['Place']['value'],'Place',get_sentiment(place['value']))

        
       # out_speech = "Done, Have a beautiful day "+str(food_sentiment)+" "+str(person_sentiment)+" "+str(place_sertiment)
        out_speech="Done, Thanks for sharing your day with me. I have updated your Emotions. Would you like to share your day again or would you like to get some suggestions? You can end this conversation by saying, Bye emotion"
        card = "ThankYou"
        reprompt = out_speech
        return build_response({}, build_speechlet_response(
            card, out_speech, reprompt, False))

    message = {}
    message['shouldEndSession'] = False
    message['directives'] = dir
    message["outputSpeech"] = {"type": "PlainText", "text": out_speech}
    message["card"] = {"type": "Simple", "title": "SessionSpeechlet - Welcome",
                       "content": "SessionSpeechlet - Hey Vikas"}
    message["reprompt"] = {"outputSpeech": {"type": "PlainText", "text": out_speech}}
    return build_response2(message)


def my_day(intent, session, dialog_state):
    arr = [0] * 6
    slots = intent['slots']
    for i, slot in enumerate(slots):
        if 'value' in slots[slot]:
            arr[i] = 1

    if dialog_state in ("STARTED", "IN_PROGRESS"):
        return continue_dialog(intent,session, arr)
    elif dialog_state == "COMPLETED":
        return statement("trip_intent", "Have a good trip")
    else:
        return statement("trip_intent", "No dialog")


def handle_session_end_request():
    card_title = "ThankYou.!"
    speech_output = "Thank you for trying My Emotion. You are a wonderful person. " \
                    "Have a nice day! "
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))
        
        
def food_connect(session):
    session_attributes = {}
    output= connect_peope_food(session,0)
    card_title = "Your Matches."
    if output=="Here are few matches. ":
        output="Sorry, we couldn't find any match. Please wait for few more days. "
        card_title="Sorry, try after few days."
    output=output + " Would you like to share your day or would you like to get some suggestions? You can end this conversation by saying, Bye emotion?"
    
    reprompt_text = output
    speech_output= output
        
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, False))
        
def place_connect(session):
    session_attributes = {}
    output= connect_peope_place(session,0)
    card_title = "Your Matches."
    if output=="Here are few matches. ":
        output="Sorry, we couldn't find any match. Please wait for few more days. "
        card_title="Sorry, try after few days."

    output=output + " Would you like to share your day or would you like to get some suggestions? You can end this conversation by saying, Bye emotion?"

    

    reprompt_text = output
    speech_output= output
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, False))

def end_it():
    session_attributes = {}
    output= "ThankYou, It was awsome talking to you."
    card_title = "ThankYou.!"

    reprompt_text = output
    speech_output= output
    should_end_session = True
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, True))

def update_phone_number(user_id):
    
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
    table = dynamodb.Table('user_id_name')
    table.update_item(
    Key={
        'ID': user_id
        },
    UpdateExpression='SET CanShare = :val1',
    ExpressionAttributeValues={
        ':val1': False
    }
    )
    
    output="Hurray, We have update your preference."
    card_title = "Done"

    reprompt_text = output
    speech_output= output
    should_end_session = False
    return build_response({}, build_speechlet_response(
        card_title, speech_output, reprompt_text, False))
def get_help():
    output="Hello.!"\
        "Welcome to My Emotion Help Centre."\
        " My emotion is an advanced Daily Logger which helps you to understand more "\
        "about yourself and to connect with people of similar interests."\
        " You can share your day by saying , I would like to share my day."\
        " You can connect with people of similar interests by saying, "\
        " Connect with someone who likes the same food as me,"\
        " or , Connect with someone who likes the same place as me."\
        " You can get to know more about yourself by saying,"\
       " What food do i like the most , or , Which place do I like the most , or , "\
        " Whom do i like the most."\
        " You can turn of contact sharing by saying, remove my phone number."\
        " At any point of conversation you can say Bye Emotion to end the conversation. ThankYou"

    card_title = 'Help Centre.'

    reprompt_text = output
    speech_output= output
    should_end_session = False
    return build_response({}, build_speechlet_response(
        card_title, speech_output, reprompt_text, False))

def food_i_like(intent, session):
    session_attributes = {}
    output= connect_peope_food(session,1)
    card_title = "Food You Like."
    output=output + " . Would you like to share your day or would you like to get some suggestions? You can end this conversation by saying, Bye emotion?"
    reprompt_text = output
    speech_output= output
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, False))
        
def person_i_like(intent, session):
    session_attributes = {}
    output= top_people(session)
    card_title = "People You Like."
    output=output + " . Would you like to share your day or would you like to get some suggestions? You can end this conversation by saying, Bye emotion?"
    reprompt_text = output
    speech_output= output
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, False))   
    
def place_i_like(intent, session):
    session_attributes = {}
    output= connect_peope_place(session,1)
    card_title = "Places You Like."
    output=output + " . Would you like to share your day or would you like to get some suggestions? You can end this conversation by saying, Bye emotion?"
    reprompt_text = output
    speech_output= output
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, False))

def get_suggestions():
    output="Here are few suggestions i can offer you . You can connect with people of similar interests by saying, "\
        " Connect with someone who likes the same food as me,"\
        " , or ,  Connect with someone who likes the same place as me."\
        " You can get to know more about yourself by saying,"\
       " What food do i like the most , or , Which place do I like the most , or , "\
        " Whom do i like the most."\
        " Please try these only after you have registered and have shared your day few times."
    session_attributes = {}
    card_title="Suggestions I can Give."
    reprompt_text = output
    speech_output= output
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, False))
        
        
        
def invalid_intent():
    output="Sorry , I dint get you. Here are the things I can help you with."\
            " My emotion is an advanced Daily Logger which helps you to understand more "\
            "about yourself and to connect with people of similar interests."\
            " You can share your day by saying , I would like to share my day."\
            " You can connect with people of similar interests by saying, "\
            " Connect with someone who likes the same food as me,"\
            " or , Connect with someone who likes the same place as me."\
            " You can get to know more about yourself by saying,"\
           " What food do i like the most , or , Which place do I like the most , or , "\
            " Whom do i like the most."\
            " You can turn of contact sharing by saying, remove my phone number."\
            " At any point of conversation you can say Bye Emotion to end the conversation. ThankYou.!"
    
    card_title = 'Help Centre'
    
    reprompt_text = output
    speech_output= output
    should_end_session = False
    return build_response({}, build_speechlet_response(
            card_title, speech_output, reprompt_text, False))

def error():
    output="I'm Sorry, I made a mistake. Could you please try again."
    card_title = "Sorry.!"
    
    reprompt_text = output
    speech_output= output
    should_end_session = False
    return build_response({}, build_speechlet_response(
            card_title, speech_output, reprompt_text, False))


# --------------- Events ------------------

def on_launch(launch_request, session):
    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    return get_welcome_response(session['user']['userId'].split('.')[3])


def on_intent(intent_request, session):
    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']
    
    if intent_name=="PersonILike":
        return person_i_like(intent, session)
    elif intent_name=="PlaceIlike":
        return place_i_like(intent, session)
    elif intent_name=="FoodIlike":
        return food_i_like(intent, session)
    elif intent_name=='DontShareNumber':
        user_id = session['user']['userId'].split('.')[3]
        return update_phone_number(user_id)
    elif intent_name=="END":
        return end_it();
    elif intent_name == "TellYourName":
        return set_name(intent, session,intent_request["dialogState"])
    elif intent_name == "MyDay":
        return my_day(intent, session, intent_request["dialogState"])
    elif intent_name == "PlaceConnect":
        return place_connect(session)
    elif intent_name == 'FoodConnect':
        return food_connect(session)
    elif intent_name == "getSuggestions":
        return get_suggestions()
    
    elif intent_name == "AMAZON.HelpIntent":
        
        return get_help()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        return invalid_intent()


def on_session_ended(session_ended_request, session):
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])




    






 

# --------------- Main handler ------------------

def lambda_handler(event, context):
    requested_application_id=event['context']['System']["application"]["applicationId"]
    application_id="amzn1.ask.skill.9e7fa601-4c3c-4c2c-8dd5-0836067cc01c"
    
    if (application_id==requested_application_id):
        try:  
            if event['request']['type'] == "LaunchRequest":
                    return on_launch(event['request'], event['session']) 
            elif event['request']['type'] == "IntentRequest":
                    return on_intent(event['request'], event['session'])
            elif event['request']['type'] == "SessionEndedRequest":
                    return on_session_ended(event['request'], event['session'])
           
            
                
        except :
            return error()
    else:
        return 403
            
    