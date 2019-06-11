Problem statement:
When a person travels to a new place, where he’s unaware of it’s beauty, people, the life. 
It can be quite a scary and sometimes a dull experience but don’t you worry, we’re here to help 
you overcome this we introduce to you the “Emotion connect” which will help you connect with people of your kind, 
people with same taste in food and tourism, won’t let you feel lonely. Introverts can make the most of the app. 

Uniqueness of the solution:
We have many apps to connect with like minded people, but what they usually do is ask the user to fill up a form,
which acts as the main source of the user interests and using the answers given by the user in the form,
they find a match but the problem with this approach is that at the time of filling the preference form , 
the user may act instantaneously and write what was good at that point of time or based on that days experience.
Emotion connect has a different approach what it does is it acts as a personal diary collecting user data
at the end of each day in the form of conversations with Emotion Connect Alexa skill. 
Based on these conversations a user has with Emotion Connect Alexa skill, we extract an entity and assign the sentiment the user has towards it,
we use nlp to extract sentiments associated with each entity (food, places) and
store the entities along with their sentiment score in a database and we match users based on their top 3 preferences in food and places they like to visit.
so, it is more data driven and provides a clearer picture as to the preferences of a user and provides a better match.

Technologies we are using:
1. Alexa Skills : To collect information about users day by having conversation with the user and to connect people with similar interests(sentiment).
2. Amazon Lambda Functions: To handle Intents and to communicate between database and Sentiment analysis api (Dandelion ).
3. Amazon DynamoDB: To securely store user information on cloud.
4. Dandelion API: To perform sentiment analysis on User information


Flow of Events
1. When the user logins in for the first time we collect his name and phone number and also ask him if 
   he is interested to connect with people or just want to use it as a Daily Logger.
2. Everyday user can share his day with Alexa, like the food he had, places to went to and people he met. 
   This information will be passed on to lambda function where we extract the sentiment of the conversation and write it to the database.
3. When the user wants to know what he likes the most we query our database and provide top three foods,
   places and people he likes. If he wishes to connect with people with similar sentiments we will query our server 
   and provide the contact information of best matches who are also willing to connect.

Demo Video : https://youtu.be/NOukRmxe4Ac
