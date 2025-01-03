import argparse
import asyncio
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


async def main():
    args = parse_args()

    # Metadata for gRPC connection
    metadata_args = [("function-id", args.function_id), ("authorization", "Bearer " + args.apikey)]
    channel = a2f_3d.client.auth.create_channel(uri="grpc.nvcf.nvidia.com:443", use_ssl=True, metadata=metadata_args)
    stub = A2FControllerServiceStub(channel)

    # Create async gRPC stream
    stream = stub.ProcessAudioStream()

    write = asyncio.create_task(a2f_3d.client.service.write_to_stream(stream, args.config, args.text))
    read = asyncio.create_task(a2f_3d.client.service.read_from_stream(stream))

    await write
    await read


if __name__ == "__main__":
    asyncio.run(main())
