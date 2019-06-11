import boto3
from boto3.dynamodb.conditions import Key, Attr

def connect_peope_food(session,just_top_food,user_credentials_table_name='user_id_name',user_emotions_table_name='user_emotion'):
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
    user_emotions_table = dynamodb.Table(user_emotions_table_name)
    user_id = session['user']['userId'].split('.')[3]
    Items = (user_emotions_table.query(
        KeyConditionExpression=Key('ID').eq(user_id))['Items']
    )
    food = []
    
    for item in Items:
        if (item['EntityType'] == 'Food') and (item['Sentiment'] > '0.5'):
            food.append((item['EntityName'], item['Sentiment']))
    
    if len(food)==0:
            return "Sorry , you havn't told me much about the food you like.!"
    
    food = sorted(food, key=lambda x: x[1], reverse=True)[:3]
    if just_top_food:
        if len(food)==0:
            return "Sorry , you havn't told me much about the food you like.!"
        return "Here you go, You seem to like " + " , ".join([fo[0] for fo in food])

    top_matches = {}
    
    if len(food)==1:
        for item in (user_emotions_table.scan(FilterExpression=((Attr('Sentiment').gt('0.5') & (
            Attr('EntityName').eq(food[0][0]))))))['Items']:
            if item['ID'] != user_id:
                if item['ID'] in top_matches:
                    top_matches[item['ID']] = top_matches[item['ID']] + item['Sentiment']
                else:
                    top_matches[item['ID']] = item['Sentiment'] 
    elif len(food)==2:
        for item in (user_emotions_table.scan(FilterExpression=((Attr('Sentiment').gt('0.5') & (
            Attr('EntityName').eq(food[0][0]) | Attr('EntityName').eq(food[1][0]) )))))['Items']:
            if item['ID'] != user_id:
                if item['ID'] in top_matches:
                    top_matches[item['ID']] = top_matches[item['ID']] + item['Sentiment']
                else:
                    top_matches[item['ID']] = item['Sentiment']
    else:
        for item in (user_emotions_table.scan(FilterExpression=((Attr('Sentiment').gt('0.5') & (
            Attr('EntityName').eq(food[0][0]) | Attr('EntityName').eq(food[1][0]) | Attr('EntityName').eq(
            food[2][0]))))))['Items']:
            

            if item['ID'] != user_id:
                if item['ID'] in top_matches:
                    top_matches[item['ID']] = top_matches[item['ID']] + item['Sentiment']
                else:
                    top_matches[item['ID']] = item['Sentiment']


    top_matches = sorted(top_matches.items(), key=lambda x: x[1])[:3]
    

        
    
    user_credentials_table = dynamodb.Table(user_credentials_table_name)
    name_ph_no="Here are few matches. "
    
    if(len(top_matches)!=0):
        for i,match in enumerate(top_matches):
            res = user_credentials_table.query(KeyConditionExpression=Key('ID').eq(match[0]))['Items'][0]
            if res['CanShare']:
                name_ph_no=name_ph_no+" Name: "+res['Name']+ ",Phone No: " +", ".join(str(res['PhNo'])) + ". "
    
    return name_ph_no

def connect_peope_place(session,just_top_place, user_credentials_table_name='user_id_name', user_emotions_table_name='user_emotion'):
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
    user_emotions_table = dynamodb.Table(user_emotions_table_name)
    user_id = session['user']['userId'].split('.')[3]
    Items = (user_emotions_table.query(
        KeyConditionExpression=Key('ID').eq(user_id))['Items']
    )
    place = []

    for item in Items:
        if (item['EntityType'] == 'Place') and (item['Sentiment'] > '0.5'):
            place.append((item['EntityName'], item['Sentiment']))

    place = sorted(place, key=lambda x: x[1], reverse=True)[:3]
    if len(place)==0:
            return "Sorry, you havn't told me much about the places you like. "
    
    if just_top_place:
        if len(place)==0:
            return "Sorry, you havn't told me much about the places you like. "
        
        return "Here you go, You seem to like " + " ,".join([pl[0] for pl in place])
    top_matches = {}
    

    if len(place)==1:
        for item in (user_emotions_table.scan(FilterExpression=((Attr('Sentiment').gt('0.5') & (
            Attr('EntityName').eq(place[0][0]) )))))['Items']:
            if item['ID'] != user_id:
                if item['ID'] in top_matches:
                    top_matches[item['ID']] = top_matches[item['ID']] + item['Sentiment']
                else:
                    top_matches[item['ID']] = item['Sentiment']
    elif len(place)==2:
        for item in (user_emotions_table.scan(FilterExpression=((Attr('Sentiment').gt('0.5') & (
            Attr('EntityName').eq(place[0][0]) | Attr('EntityName').eq(place[1][0])  )))))['Items']:
            if item['ID'] != user_id:
                if item['ID'] in top_matches:
                    top_matches[item['ID']] = top_matches[item['ID']] + item['Sentiment']
                else:
                    top_matches[item['ID']] = item['Sentiment']
    else:
        for item in (user_emotions_table.scan(FilterExpression=((Attr('Sentiment').gt('0.5') & (
            Attr('EntityName').eq(place[0][0]) | Attr('EntityName').eq(place[1][0]) | Attr('EntityName').eq(
        place[2][0]))))))['Items']:
            if item['ID'] != user_id:
                if item['ID'] in top_matches:
                    top_matches[item['ID']] = top_matches[item['ID']] + item['Sentiment']
                else:
                    top_matches[item['ID']] = item['Sentiment']

    top_matches = sorted(top_matches.items(), key=lambda x: x[1])[:3]
    user_credentials_table = dynamodb.Table(user_credentials_table_name)
    name_ph_no="Here are few matches. "
    if(len(top_matches)!=0):
        for match in top_matches:
            res = user_credentials_table.query(KeyConditionExpression=Key('ID').eq(match[0]))['Items'][0]
            if res['CanShare']:
                name_ph_no=name_ph_no+" Name: "+res['Name']+ ",Phone No: " +", ".join(str(res['PhNo'])) + ". "
    return name_ph_no

def top_people(session, user_credentials_table_name='user_id_name', user_emotions_table_name='user_emotion'):
    dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
    user_emotions_table = dynamodb.Table(user_emotions_table_name)
    user_id = session['user']['userId'].split('.')[3]
    Items = (user_emotions_table.query(
        KeyConditionExpression=Key('ID').eq(user_id))['Items']
    )
    people = []

    for item in Items:
        if (item['EntityType'] == 'People') and (item['Sentiment'] > '0.5'):
            people.append((item['EntityName'], item['Sentiment']))
    
    people = sorted(people, key=lambda x: x[1], reverse=True)[:3]
    if len(people)==0:
        return "Sorry , you hanv't told me much about people you like"
    else:
        return "Here you go, You seem to like " + " , ".join([po[0] for po in people])
        
        
        
