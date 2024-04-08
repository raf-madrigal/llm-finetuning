from pyht import Client
from dotenv import load_dotenv
from pyht.client import TTSOptions
import tempfile
import wave
import os
load_dotenv()

client = Client(
    user_id=os.environ['PYHT_USER_ID'], 
    api_key=os.environ['PYHT_SECRET']
)

# text_to_convert = "Can you tell me your account email or, ah your phone number?"
options = TTSOptions(voice=os.environ['PYHT_SNOOP_CLONED_VOICE'])

def text_to_speech(text_to_convert):

    client = Client(
    user_id=os.environ['PYHT_USER_ID'], 
    api_key=os.environ['PYHT_SECRET']
    )

    options = TTSOptions(voice=os.environ['PYHT_SNOOP_CLONED_VOICE'])

    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as fp:
        with wave.open(fp, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(22050)

            # for chunk in self.playht_clie
            for chunk in client.tts(text_to_convert, options):
                wf.writeframes(chunk)

        audio_file_path = fp.name

    return audio_file_path

