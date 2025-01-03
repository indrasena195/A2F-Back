import asyncio
import websockets
import json

# Store connected WebSocket clients
clients = set()

async def handle_websocket(websocket):
    print("conneted")
    # Add the new client to the set of connected clients
    clients.add(websocket)
    try:
        async for message in websocket:
            try:
                data = json.loads(message)
                print(f"Received data: {data}")
                
                # Broadcast the data to all connected clients
                await broadcast_data(data)
            except json.JSONDecodeError:
                print("Received invalid JSON data")
    except websockets.ConnectionClosedError:
        print("Connection closed unexpectedly")
    finally:
        # Remove the client from the set when disconnected
        clients.remove(websocket)

async def broadcast_data(data):
    # Create a list of coroutines for sending the data to each client
    tasks = [client.send(json.dumps(data)) for client in clients]
    
    # Use asyncio.gather to execute all tasks concurrently
    if tasks:  # Check if there are any tasks to execute
        await asyncio.gather(*tasks)

async def main():
    async with websockets.serve(handle_websocket, "localhost", 5555):
        print("WebSocket server is running on ws://localhost:5555")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
