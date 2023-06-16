from Bard import Chatbot
from playsound import playsound
import speech_recognition as sr
from os import system
import whisper
import warnings
import sys
import argostranslate.package
import argostranslate.translate


# Paste your Bard Token (check README.md for where to find yours) 
token = "XQjMGt9OQJx2nNHyK3XfUSMfPfaEO8wbkaYH0fQZJDT9xfjALkrvXetENDx49DL9G7-KVg."
# Initialize Google Bard API
chatbot = Chatbot(token)
# Initialize speech recognition
r = sr.Recognizer()
# Initialize Whisper model
tiny_model = whisper.load_model('tiny')
base_model = whisper.load_model('base')
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU; using FP32 instead")

# Initiate pyttsx3 if not running Mac OS
if sys.platform != 'darwin':
    import pyttsx3
    engine = pyttsx3.init() 
    # Get the current speech rate
    rate = engine.getProperty('rate')
    # Decrease speech rate by 50 words per minute (Change as desired)
    engine.setProperty('rate', rate-50) 

def prompt_bard(prompt):
    response = chatbot.ask(prompt)
    return response['content']

def speak(text):
    # If Mac OS use system messages for TTS
    if sys.platform == 'darwin':
        ALLOWED_CHARS = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,?!-_$: ")
        clean_text = ''.join(c for c in text if c in ALLOWED_CHARS)
        system(f"say '{clean_text}'")
    # Use pyttsx3 for other operating sytstems
    else:        
        engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_ES-MX_SABINA_11.0')#voice local
        engine.say(text)
        engine.runAndWait()

def speak_azure(speak):
    import azure.cognitiveservices.speech as speechsdk

    # Creates an instance of a speech config with specified subscription key and service region.
    speech_key = "c55c6d9bb32245c69d81af8285c92257"
    service_region = "eastus"

    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    # Note: the voice setting will not overwrite the voice element in input SSML.
    #speech_config.speech_synthesis_voice_name = "es-MX-JorgeNeural"
    speech_config.speech_synthesis_voice_name = "es-MX-LarissaNeural"

    text = speak

    # use the default speaker as audio output.
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

    result = speech_synthesizer.speak_text_async(text).get()
    # Check result
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized for text [{}]".format(text))
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))

def speak_google(speak_text):
    from gtts import gTTS
    tts = gTTS(text=speak_text, lang='es')
    tts.save("audio_google.mp3")
    from pydub import AudioSegment
    from pydub.playback import play
    audio = AudioSegment.from_file("audio_google.mp3")
    play(audio)
    
def en_es(text_en_es):
    from_code = "en"
    to_code = "es"
    return argostranslate.translate.translate(text_en_es, from_code, to_code)

def es_en(text_es_en):
    from_code = "es"
    to_code = "en"
    return argostranslate.translate.translate(text_es_en, from_code, to_code)   

def main():
    # Initialize microphone object
    with sr.Microphone() as source:#micro disponible
        r.adjust_for_ambient_noise(source)
        # Runs program indefinitely
        #playsound("open.mp3")
        while True:
            print('\n"Google: En el momento que me necesites, di "¡Hola, Google!" para activarme. \n')
            #speak('En el momento que me necesites, di "¡Hola, Google!" para activarme.')
            speak_google('En el momento que me necesites, di "¡Hola, Google!" para activarme.')
            #speak_azure('En el momento que me necesites, di "¡Hola, Google!" para activarme.')
            # Continuously listens for wake word locally
            while True:
                audio = r.listen(source)
                try:                                                        
                    with open("wake_detect.wav", "wb") as f:
                        f.write(audio.get_wav_data())
                    # Transcribe wake word using whisper tiny model
                    result = base_model.transcribe('wake_detect.wav')
                    text_input = result['text']
                    # If wake word is found, break out of loop
                    print("Tú: " + text_input)
                    if 'hola' in text_input.lower().strip():
                        # Play wake word detected notification sound (faster than TTS)                        
                        print("Google: Palabra de activación detectada. ¿En qué te puedo ayudar?. \n")
                        #speak("Palabra de activación detectada. ¿En qué te puedo ayudar?.")
                        speak_google("Palabra de activación detectada. ¿En qué te puedo ayudar?.")       
                        #speak_azure("Palabra de activación detectada. ¿En qué te puedo ayudar?.") 
                        break
                    else:
                        #playsound("wrongKey.mp3")
                        print("Google: No se encontró ninguna palabra de activación. Seguiré escuchando...")#       
                except Exception as e:
                    #playsound("errorTranscribingAudio.mp3")
                    print("Error transcribing audio: ", e)
                    continue

            try:
                while True:                    
                    playsound('wake_detected.mp3')
                    # Record prompt
                    audio = r.listen(source)
                    with open("prompt.wav", "wb") as f:
                        f.write(audio.get_wav_data())
                    # Transcribe prompt using whisper base model
                    result = base_model.transcribe('prompt.wav')
                    prompt_text = result['text']                                    
                    #playsound("sending.mp3")
                    # If prompt is empty, start listening for wake word again
                    if len(prompt_text.strip()) == 0:
                        #playsound("emptyPrompt.mp3")        
                        print("Google: Mensaje vacío. Por favor, hable de nuevo.")
                        #speak("Mensaje vacío. Por favor, hable de nuevo.") 
                        speak_google("Mensaje vacío. Por favor, hable de nuevo.") # voz google                      
                        #speak_azure("Mensaje vacío. Por favor, hable de nuevo.") # voz microsoft                 
                        continue
                    else:
                        if 'gracias' in prompt_text.lower().strip():
                            # Play wake word detected notification sound (faster than TTS)                        
                            print("Google: De nada, ¡Adios!. \n")
                            #speak("De nada, ¡Adios!.")
                            speak_google("De nada, ¡Adios!.")
                            #speak_azure("De nada, ¡Adios!.") # voz microsoft       
                            break
                                            
                        print("Sending:", prompt_text, '\n')
                        # translateBefore
                        translateEsEn = es_en(prompt_text)
                        # Prompt Bard. 
                        response = prompt_bard(translateEsEn)
                        # translateAfter
                        translateEnEs = en_es(response)           
                        # Prints Bard response normal if windows (cannot ASCII delete in command prompt to change font color)
                        if sys.platform.startswith('win'):
                            #playsound("bardResponseNotification.mp3")
                            print('Response: ', translateEnEs)
                        else:
                            # Prints Bard response in red for linux & mac terminal
                            print("\033[31m" + 'Response: ', translateEnEs, '\n' + "\033[0m")
                        #speak(translateEnEs)# voz pc
                        speak_google(translateEnEs) # voz google
                        #speak_azure(translateEnEs) # voz microsoft
            except Exception as e:
                #playsound("errorTranscribingAudio.mp3")
                print("Error transcribing audio: ", e)
                continue            
            
if __name__ == '__main__':
    main()