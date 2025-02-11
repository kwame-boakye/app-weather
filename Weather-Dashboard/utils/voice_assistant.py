import speech_recognition as sr
import pyttsx3
import threading
from utils.logger import logger


class WeatherVoiceAssistant:
    def __init__(self):
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()

        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 150)  # Speed of speech
        self.engine.setProperty("volume", 0.9)

        # Get available voices and set a natural sounding one
        voices = self.engine.getProperty("voices")
        self.engine.setProperty("voice", voices[0].id)  # Index 0 is usually default

        self.is_listening = False
        self.commands = {
            "weather": ["what's the weather", "how's the weather", "weather today"],
            "forecast": ["show forecast", "weather forecast", "next days"],
            "temperature": [
                "what's the temperature",
                "how hot is it",
                "how cold is it",
            ],
        }

    def start_listening(self, callback):
        """Start listening for voice commands in background"""
        self.is_listening = True
        threading.Thread(
            target=self._listen_loop, args=(callback,), daemon=True
        ).start()

    def stop_listening(self):
        """Stop listening for voice commands"""
        self.is_listening = False

    def _listen_loop(self, callback):
        """Continuous listening loop"""
        with sr.Microphone() as source:
            # Adjust for ambient noise
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

            while self.is_listening:
                try:
                    logger.info("Listening for voice command...")
                    audio = self.recognizer.listen(
                        source, timeout=5, phrase_time_limit=5
                    )

                    text = self.recognizer.recognize_google(audio).lower()
                    logger.info(f"Recognized: {text}")

                    command = self._parse_command(text)
                    if command:
                        callback(command)

                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    logger.debug("Could not understand audio")
                    continue
                except sr.RequestError as e:
                    logger.error(f"Could not request results: {str(e)}")
                    self.speak("I'm having trouble connecting to the speech service")
                except Exception as e:
                    logger.error(f"Error in voice recognition: {str(e)}")

    def _parse_command(self, text):
        """Parse voice input into command"""
        for command_type, phrases in self.commands.items():
            if any(phrase in text for phrase in phrases):
                if "in" in text and "in" != text[-2:]:
                    # Extract location if specified (e.g., "weather in London")
                    location = text.split("in")[-1].strip()
                    return {"type": command_type, "location": location}
                return {"type": command_type}
        return None

    def speak(self, text):
        """Convert text to speech"""
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            logger.error(f"Error in text-to-speech: {str(e)}")

    def speak_weather(self, weather_data):
        """Speak current weather conditions"""
        try:
            temp = weather_data["main"]["temp"]
            desc = weather_data["weather"][0]["description"]
            humidity = weather_data["main"]["humidity"]

            text = (
                f"The current temperature is {temp:.1f} degrees Celsius. "
                f"Weather conditions are {desc}. "
                f"Humidity is {humidity} percent."
            )

            self.speak(text)
        except Exception as e:
            logger.error(f"Error speaking weather: {str(e)}")
            self.speak("I'm having trouble reading the weather data")

    def speak_forecast(self, forecast_data):
        """Speak weather forecast"""
        try:
            today = forecast_data["list"][0]
            temp = today["main"]["temp"]
            desc = today["weather"][0]["description"]

            text = (
                f"The forecast shows {desc} with a temperature "
                f"of {temp:.1f} degrees Celsius."
            )

            self.speak(text)
        except Exception as e:
            logger.error(f"Error speaking forecast: {str(e)}")
            self.speak("I'm having trouble reading the forecast data")
