# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# import argparse, asyncio
# import a2f_3d.client.auth
# import a2f_3d.client.service
# from nvidia_ace.services.a2f_controller.v1_pb2_grpc import A2FControllerServiceStub

# def parse_args() -> argparse.Namespace:
#     parser = argparse.ArgumentParser(
#                         description="Sample python application to send audio and receive animation data and emotion data through the Audio2Face-3D API.",
#                         epilog="NVIDIA CORPORATION.  All rights reserved.")
#     parser.add_argument("file", help="PCM-16 bits single channel audio file in WAV ccontainer to be sent to the Audio2Face-3D service")
#     parser.add_argument("config", help="Configuration file for inference models")
#     parser.add_argument("--apikey", type=str, required=True, help="NGC API Key to invoke the API function")
#     parser.add_argument("--function-id", type=str, required=True, default="", help="Function ID to invoke the API function")
#     return parser.parse_args()

# async def main():
#     args = parse_args()

#     metadata_args = [("function-id", args.function_id), ("authorization", "Bearer " + args.apikey)]
#     # Open gRPC channel and get Audio2Face-3D stub
#     channel = a2f_3d.client.auth.create_channel(uri="grpc.nvcf.nvidia.com:443", use_ssl=True, metadata=metadata_args)
            
#     stub = A2FControllerServiceStub(channel)

#     stream = stub.ProcessAudioStream()
#     write = asyncio.create_task(a2f_3d.client.service.write_to_stream(stream, args.config, args.file))
#     read = asyncio.create_task(a2f_3d.client.service.read_from_stream(stream))

#     await write
#     await read

# if __name__ == "__main__":
#     asyncio.run(main())





# import argparse
# import asyncio
# import os
# import requests
# import a2f_3d.client.auth
# import a2f_3d.client.service
# from nvidia_ace.services.a2f_controller.v1_pb2_grpc import A2FControllerServiceStub
# import azure.cognitiveservices.speech as speechsdk

# # Flowise API URL
# FLOWISE_API_URL = "http://localhost:3000/api/v1/prediction/8b0b7f9e-56a0-4113-aaa6-bebdb062c395"

# def parse_args() -> argparse.Namespace:
#     parser = argparse.ArgumentParser(
#         description="Sample python application to send text, query Flowise, receive audio, and process animation data through the Audio2Face-3D API.",
#         epilog="NVIDIA CORPORATION. All rights reserved."
#     )
#     parser.add_argument("text", help="Text input to query Flowise and process with the Audio2Face-3D service")
#     parser.add_argument("config", help="Configuration file for inference models")
#     parser.add_argument("--apikey", type=str, required=True, help="NGC API Key to invoke the API function")
#     parser.add_argument("--function-id", type=str, required=True, default="", help="Function ID to invoke the API function")
#     return parser.parse_args()

# def query_flowise(question: str) -> str:
#     response = requests.post(FLOWISE_API_URL, json={"question": question})
#     if response.status_code == 200:
#         return response.json().get("text", "")
#     else:
#         raise Exception(f"Error querying Flowise API: {response.status_code}, {response.text}")

# def text_to_speech(text: str, output_file: str) -> str:
#     # Setup Azure TTS
#     speech_config = speechsdk.SpeechConfig(
#         endpoint=f"wss://{os.getenv('SPEECH_REGION')}.tts.speech.microsoft.com/cognitiveservices/websocket/v2",
#         subscription=os.getenv("SPEECH_KEY")
#     )
#     speech_config.speech_synthesis_voice_name = "en-US-BrianMultilingualNeural"
#     audio_config = speechsdk.audio.AudioOutputConfig(filename=output_file)

#     # Create speech synthesizer
#     synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

#     # Synthesize speech to file
#     result = synthesizer.speak_text_async(text).get()
#     if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
#         print(f"Speech synthesized to {output_file}")
#     else:
#         raise Exception(f"Error synthesizing speech: {result.reason}")

#     return output_file

# async def main():
#     args = parse_args()

#     # Query Flowise with the input text
#     print(f"Command text: {args.text}")
#     try:
#         flowise_response = query_flowise(args.text)
#         print(f"Flowise response: {flowise_response}")
#     except Exception as e:
#         print(f"Failed to get response from Flowise: {e}")
#         return

#     # Convert Flowise response to speech
#     audio_file = "output_audio.wav"
#     try:
#         audio_file = text_to_speech(flowise_response, audio_file)
#     except Exception as e:
#         print(f"Failed to synthesize speech: {e}")
#         return

#     metadata_args = [
#         ("function-id", args.function_id),
#         ("authorization", "Bearer " + args.apikey)
#     ]
#     # Open gRPC channel and get Audio2Face-3D stub
#     channel = a2f_3d.client.auth.create_channel(uri="grpc.nvcf.nvidia.com:443", use_ssl=True, metadata=metadata_args)
            
#     stub = A2FControllerServiceStub(channel)

#     stream = stub.ProcessAudioStream()
#     write = asyncio.create_task(a2f_3d.client.service.write_to_stream(stream, args.config, audio_file))
#     read = asyncio.create_task(a2f_3d.client.service.read_from_stream(stream))

#     await write
#     await read

# if __name__ == "__main__":
#     asyncio.run(main())



import argparse
import asyncio
import os
import io
import wave
import azure.cognitiveservices.speech as speechsdk
from nvidia_ace.services.a2f_controller.v1_pb2_grpc import A2FControllerServiceStub
import a2f_3d.client.auth
import a2f_3d.client.service


def parse_args():
    parser = argparse.ArgumentParser(description="Stream audio chunks to Audio2Face API.")
    parser.add_argument("text", help="Text to synthesize and stream")
    parser.add_argument("config", help="Configuration file for inference models")
    parser.add_argument("--apikey", type=str, required=True, help="NGC API Key to invoke the API function")
    parser.add_argument("--function-id", type=str, required=True, help="Function ID to invoke the API function")
    return parser.parse_args()


async def synthesize_audio_chunks(text):
    """Synthesize text to speech and yield audio chunks."""
    speech_config = speechsdk.SpeechConfig(
        subscription=os.getenv("SPEECH_KEY"),
        region=os.getenv("SPEECH_REGION"),
    )
    speech_config.speech_synthesis_voice_name = "en-US-BrianMultilingualNeural"
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)

    # Synthesize text to speech
    stream = speechsdk.AudioDataStream(synthesizer.speak_text_async(text).get())
    buffer = io.BytesIO()

    # Save synthesized audio to buffer
    stream.save_to_wave_buffer(buffer)
    buffer.seek(0)

    # Read and yield audio chunks
    with wave.open(buffer, "rb") as wav_file:
        chunk_size = 1024  # Define the chunk size (bytes)
        while chunk := wav_file.readframes(chunk_size):
            yield chunk


async def main():
    args = parse_args()

    # Metadata for gRPC connection
    metadata_args = [("function-id", args.function_id), ("authorization", "Bearer " + args.apikey)]

    channel = a2f_3d.client.auth.create_channel(uri="grpc.nvcf.nvidia.com:443", use_ssl=True, metadata=metadata_args)
    
    stub = A2FControllerServiceStub(channel)

    # Create async gRPC stream
    stream = stub.ProcessAudioStream()

    # Generate audio chunks from text input
    audio_chunks = synthesize_audio_chunks(args.text)

    # Stream audio chunks to the service
    write = asyncio.create_task(a2f_3d.client.service.write_to_stream(stream, args.config, audio_chunks))
    read= asyncio.create_task(a2f_3d.client.service.read_from_stream(stream))

    await write
    await read


if __name__ == "__main__":
    asyncio.run(main())
