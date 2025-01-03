# import os
# import requests
# import azure.cognitiveservices.speech as speechsdk

# # Flowise API URL
# FLOWISE_API_URL = "http://localhost:3000/api/v1/prediction/8b0b7f9e-56a0-4113-aaa6-bebdb062c395"

# # Query the Flowise API
# def query_flowise(question):
#     response = requests.post(FLOWISE_API_URL, json={"question": question})
#     if response.status_code == 200:
#         return response.json().get("text", "")
#     else:
#         raise Exception(f"Error querying Flowise API: {response.status_code}, {response.text}")

# # Get user input
# user_input = input("Enter your question: ")

# # Query Flowise with the user's input
# try:
#     flowise_response = query_flowise(user_input)
#     print(f"Flowise response: {flowise_response}")
# except Exception as e:
#     print(f"Failed to get response from Flowise: {e}")
#     exit()

# # Setup Azure TTS
# speech_config = speechsdk.SpeechConfig(
#     endpoint=f"wss://{os.getenv('SPEECH_REGION')}.tts.speech.microsoft.com/cognitiveservices/websocket/v2",
#     subscription=os.getenv("SPEECH_KEY")
# )
# speech_config.speech_synthesis_voice_name = "en-US-BrianMultilingualNeural"
# speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

# # Create TTS request with text stream input
# tts_request = speechsdk.SpeechSynthesisRequest(
#     input_type=speechsdk.SpeechSynthesisRequestInputType.TextStream
# )
# tts_task = speech_synthesizer.speak_async(tts_request)

# # Stream Flowise response to TTS
# tts_request.input_stream.write(flowise_response)
# tts_request.input_stream.close()

# # Wait for TTS to complete
# result = tts_task.get()
# print("[TTS END]")

import os
import requests
import azure.cognitiveservices.speech as speechsdk
import subprocess
import tempfile
import io

# Flowise API URL
FLOWISE_API_URL = "http://localhost:3000/api/v1/prediction/8b0b7f9e-56a0-4113-aaa6-bebdb062c395"

# Query the Flowise API
def query_flowise(question):
    response = requests.post(FLOWISE_API_URL, json={"question": question})
    if response.status_code == 200:
        return response.json().get("text", "")
    else:
        raise Exception(f"Error querying Flowise API: {response.status_code}, {response.text}")

# Callback function for PushAudioOutputStream
def push_audio_callback(audio_data, user_data):
    user_data.write(audio_data)

# Stream Azure TTS output and process chunks
def stream_tts_and_process(speech_config, text, config_file, api_key, function_id):
    # Create an in-memory buffer to store audio data
    buffer = io.BytesIO()

    # Create the PushAudioOutputStream using the callback
    audio_stream = speechsdk.audio.PushAudioOutputStream.create_push_stream(push_audio_callback, buffer)

    # Create AudioConfig with the audio stream
    audio_config = speechsdk.audio.AudioConfig(use_default_speaker=False, stream=audio_stream)

    # Initialize the speech synthesizer with the AudioConfig
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    # Start synthesizing text to speech
    print("Starting TTS streaming...")
    result = speech_synthesizer.speak_text_async(text).get()

    if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
        raise Exception("Speech synthesis failed.")

    print("TTS streaming completed. Processing audio...")

    # Process the audio buffer in chunks
    buffer.seek(0)
    process_audio_chunk(buffer, config_file, api_key, function_id)

# Function to process audio chunk with nim_a2f_client.py
def process_audio_chunk(chunk, config_file, api_key, function_id):
    # Save the audio buffer as a temporary .wav file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav_file:
        temp_wav_file.write(chunk.getvalue())
        temp_wav_file.close()  # Ensure the file is closed before passing it to the process

        # Run nim_a2f_client.py using the temporary .wav file
        print(f"Processing audio chunk: {temp_wav_file.name}")
        process = subprocess.Popen(
            [
                "python", "./nim_a2f_client.py", temp_wav_file.name, config_file,
                "--apikey", api_key, "--function-id", function_id
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # Capture the output and error (if any) from the process
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            print(f"Error during processing: {stderr.decode()}")
        else:
            print(f"Processing output: {stdout.decode()}")

        # After processing, remove the temporary file
        os.remove(temp_wav_file.name)
        print(f"Temporary file {temp_wav_file.name} removed.")

# Main workflow
if __name__ == "__main__":
    # Get user input
    user_input = input("Enter your question: ")

    # Query Flowise
    try:
        flowise_response = query_flowise(user_input)
        print(f"Flowise response: {flowise_response}")
    except Exception as e:
        print(f"Failed to get response from Flowise: {e}")
        exit()

    # Setup Azure TTS
    speech_config = speechsdk.SpeechConfig(
        endpoint=f"wss://{os.getenv('SPEECH_REGION')}.tts.speech.microsoft.com/cognitiveservices/websocket/v2",
        subscription=os.getenv("SPEECH_KEY")
    )
    speech_config.speech_synthesis_voice_name = "en-US-BrianMultilingualNeural"

    # Stream TTS and process with nim_a2f_client.py
    config_file = "./config/config_mark.yml"
    api_key = "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"
    function_id = "945ed566-a023-4677-9a49-61ede107fd5a"

    try:
        stream_tts_and_process(speech_config, flowise_response, config_file, api_key, function_id)
    except Exception as e:
        print(f"Error during TTS streaming and processing: {e}")
