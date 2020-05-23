import speech_recognition as sr
from IPython.display import *
from gtts import gTTS
import os
from playsound import playsound
import datetime
from datetime import date
import webbrowser
import time
import json
import requests
import imdb
import random
import urllib3
from espeak import espeak


# Setting a helper variable so the program can run infinitely (until someone force quits)
running = True

# True if debug messages should be printed
debug_mode = True

# True if speech output of intents should be given
run_audio=True


# Initializing recognizer instance and a microphone as a source
rec = sr.Recognizer()
mic = sr.Microphone()


####Basic Functions#########

def error_message():
    
    response = "Ich habe Sie nicht richtig verstanden. Beginnen wir noch mal von vorne."
    print(response)
    espeak.synth(response)
	

def welcome():
    
    response = "Herzlich willkommen! Mein Name ist Alex und ich bin Ihr Audio-Guide. In kürze können Sie sich über die jeweiligen Stationen informieren."
    print(response)
    espeak.synth(response)
    
def ready():
    
    response = "Wie kann ich Ihnen behilflich sein?"
    print(response)
    espeak.synth(response)


def make_accustic_response(resp):
    
    espeak.synth(resp)


#####IMDB-Functions#################

#############################################################
# Function for getting informations about a specific movie. #
#############################################################

# gives info about a specific movie (genres, plot, actors, director, release date)
def imdb_search(this_movie):
    print("\nSuche nach Film: {}".format(this_movie))
    
    # Looking for the movie with the given title (Problem: If there are multiple movies with the same title it, picks the first one.)
    i_movie = imdb.IMDb()
    movies = i_movie.search_movie(this_movie)
    movie = i_movie.get_movie(movies[0].movieID)
    
    print("Ich habe folgenden Film gefunden: {}\n".format(movies[0]))
    
    response = "Ich habe den Film " + str(movies[0]) + " gefunden."
    print(response)
    if run_audio == True:
        make_accustic_response(response)
   
    
    try:
        print("\nGenres:\n")
        for genre in movie['genres']:
            print(genre)
    except KeyError:
        print("\nKein Genre bekannt.")
    
    try:
        # Print the plot summary
        print("\nHandlung:\n{}".format(movie['plot'][0]))
    except KeyError:
        print("\nKeine Handlung bekannt.")
    
    try:
        # Print the cast members
        print("\nSchauspieler:\n")
        for actor in movie['cast'][:5]:#looks at the first five actors
            print("{0} as {1}".format(actor['name'], actor.currentRole))
    except KeyError:
        print("\nKeine Schauspieler bekannt.")
    
    try:
        # Print the director(s)
        if movie['directors'] is not None:
            print("\nRegisseur: {}\n".format(movie['director'][0]))
    except KeyError:
        print("\nKein Regisseur bekannt.")

    try:
        # Print the release date
        print("\nErscheinungsdatum: {}\n".format(movie['original air date']))
    except KeyError:
        print("\nErscheinungstermin unbekannt.")

###################################################################
# Function for looking for the top 10 movies in a specific genre. #
###################################################################

# searches through the imdb top 250 list for a specific genre 
def imdb_genre(this_genre):

    print("\nIch suche nach Filmen mit Genre '{}'. (Das kann etwas dauern)".format(this_genre))
    
    
    response = "Jetzt such ich 3 Filme mit Genre " + str(this_genre)
    print(response)
    if run_audio == True:
        make_accustic_response(response)
   
    
    # Getting a list of the top 250 movies (This number is the only option with the IMDb python library.)
    i_movie = imdb.IMDb()
    movielist = i_movie.get_top250_movies()
    count = 0
    listed_movies = []
    while count < 3:
        
        
        # Searching for a new random number
        while True:
            ranking = random.randint(0, 249)
            if ranking not in listed_movies:
                listed_movies.append(ranking)
                break
        
        movie = i_movie.get_movie(movielist[ranking].movieID)
        for genre in movie['genres']:
            # Checking if the first genre matches the genre the user was looking for
            if genre.lower() == this_genre:
                count += 1
                print("{0}. {1}".format(count, movie['title']))
                if run_audio == True:
                    response = movie['title']
                    espeak.synth(response)
                
                     
    print("Das sollte fürs erste genügen :)")



####Intent-Pool##########

################################################################################################################
# After receiving a request the program looks through its intent file and matches the request with a response. #
################################################################################################################

# compares the speech of the user with intents from json file
def intents(req):
    if debug_mode == True:
        print("DEBUG 6: Recognized: {}".format(req))
        print("DEBUG 7: In intents function")
   
    
    # open json file
    with open('intents.json') as json_file:
        # Loading the intent json file
        data = json.load(json_file)

        if debug_mode == True:
            print("DEBUG 8: Looking through intents in the json file")
        
        # Going through all the intents until a match is found
        for i in data['intents']:
            # Finding the right request
            for p in i['patterns']:
                if req == p.lower():
                    if debug_mode == True:
                        print("DEBUG 9: Request matches intent. Looking for response")
                    
                    # Picking a randomized response for that request
                    index = random.randint(0, len(i['responses'])-1)
                    
                    if debug_mode == True:
                        print("DEBUG 10: Found a response. About to send it to tts")
                    
                    response = i['responses'][index]
                    #tts = gTTS(response, lang='de')
                    
                    if debug_mode == True:
                        print("DEBUG 11: This is the response i should give the user")
                        print(response)
                    
                    if run_audio == True:
                        make_accustic_response(response)
                                    
                
                    # If the user is looking for a movie/genre another input is needed
                    if i['tag'] == "imdb_search":
                        request = mic_recognition(rec, mic)
                        if request['error'] is None:
                            imdb_search(request['response_trans'].lower())
                            
                    elif i['tag'] == "imdb_genre":
                        request = mic_recognition(rec, mic)
                        if request['error'] is None:
                            imdb_genre(request['response_trans'].lower())
                            
                    # If the user wishes to exit the program
                    elif i['tag'] == "bye":
                        return True
                    
                    return False
        
        # If the request does not match an intent the user has to repeat their query
        
        print("Error: I understood '{}'".format(req))
        #tts = gTTS('Verzeihung, aber ich verstehe Ihre Anfrage nicht. Probieren wir es nochmals von Anfang an!', lang='de')
        
        response="Verzeihung, aber ich verstehe Ihre Anfrage nicht. Probieren wir es nochmals von Anfang an!"
        if debug_mode == True:
            print("DEBUG 12: This is the response i should give the user")
            print("DEBUG - Error: {}".format(response))
            
        if run_audio == True:
            make_accustic_response(response)
        
        return False
		
		
	
		
		

####SPEECH_RECOGNITION##################################

#####AUDIOINPUT PARSER###############

#################################################################################################################
# Here the program makes a recognizer query and checks for different errors and returns a response accordingly. #
#################################################################################################################

def mic_recognition(recognizer, microphone):
    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(microphone, sr.Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")
        
    response = {
      "response_trans": None,
      "error": None
    }
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio_recorded = recognizer.listen(source)
    try:
        response["response_trans"] = recognizer.recognize_google(audio_recorded, language = "de-DE")
    except sr.RequestError:
        #API was unreachable or unresponsive
        response["error"] = "ERROR: Die API ist nicht verfügbar."
    except sr.UnknownValueError:
        #speech was unintelligible
        response["error"] = "ERROR: Der Audio-Guide konnte den Sprach-Input nicht verstehen."
        
    return response

####SpeechRecognition##########
##########################################################################################################
# This is where the user interaction takes place. The program welcomes the user and waits for a request. #
##########################################################################################################

def activate_speechrec():
    if debug_mode == True:
        print("DEBUG 3: In activate_speechrec. Sending welcome message.")
    
    welcome()
    
    while True:
        ready()
        
        if debug_mode == True:
            print("DEBUG 4: In activate_speechrec while loop. Ready for request.")
        
        request = mic_recognition(rec, mic)
       
        # If the program recognizes a voice it enters the intents function to look for a proper response
        if request["error"] is None:
            
            if debug_mode == True:
                print("DEBUG 5: Got a request. Going into intents function.")
            
            # if speech was understood --> into intents function
            stop = intents(request["response_trans"].lower())
            if stop == True:
                break
        else:
            print(request["error"])
            error_message()



#######VOICE ACTIVATION##########################
#############################################################
# This is where the chat bot starts listening for any input #
#############################################################

def program():
    # Setting the keyword and other helper variables to keep the program running
    keyword = "hallo alex"
    success = False
    running = True
    
    # Program listens for the keyword to start an interaction with the user
    while running:
        print("Ich bin bereit ...")
        request = mic_recognition(rec, mic)

        # Check if the voice input has been recognized
        if request["error"] is None:
            if request["response_trans"].lower() == keyword:
                success = True
                
                if debug_mode == True:
                    print("DEBUG 1: Recognized keyword")
                
                break
            else:
                print("ERROR: I understood: {}".format(request["response_trans"].lower()))

    # Now that the keyword has been recognized (or not) the user interaction begins
    if success is True and running is True:
        
        if debug_mode == True:
            print("DEBUG 2: Entering activate_speechrec function")
        
        activate_speechrec()
    
    else:
        print(request["error"])
        error_message()

        
		
		
############################################################
# This keeps the program running until someone force quits #
############################################################

while running:
    program()




