import requests

def azure_text_to_speech_stream(text):
    subscription_key = "464ad874589040bbb1a107c263027973"
    region = "southeastasia"
    endpoint = f"https://{region}.tts.speech.microsoft.com/cognitiveservices/v1"
    
    headers = {
        "Content-Type": "application/ssml+xml",
        "Ocp-Apim-Subscription-Key": subscription_key,
        "X-Microsoft-OutputFormat": "riff-16khz-16bit-mono-pcm",
    }
    
    body = f"""
    <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>
        <voice name='en-US-JennyNeural'>{text}</voice>
    </speak>
    """
    
    # Send POST request to Azure TTS API
    response = requests.post(endpoint, headers=headers, data=body)
    
    if response.status_code != 200:
        raise Exception(f"Azure TTS API request failed. Status code: {response.status_code}")
    
    return response.content  # The response content is the audio stream.

def save_audio_to_file(audio_data, file_path):
    with open(file_path, "wb") as file:
        file.write(audio_data)
    print(f"Audio saved to {file_path}")

# Example usage
text = "Hello, how are you?"
audio_data = azure_text_to_speech_stream(text)

# Save the audio stream to a WAV file
save_audio_to_file(audio_data, "output_audio.wav")
