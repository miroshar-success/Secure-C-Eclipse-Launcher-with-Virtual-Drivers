import asyncio
import websockets
import os

SERVER_HOST = "localhost"
SERVER_PORT = 8765
PROJECT_DIR = "path/to/your/project"

async def send_project(websocket, path):
    try:
        async for message in websocket:
            if message == "REQUEST_PROJECT":
                project_files = []
                for root, dirs, files in os.walk(PROJECT_DIR):
                    for file in files:
                        with open(os.path.join(root, file), "rb") as f:
                            project_files.append(f.read())
                
                project_code = b''.join(project_files)
                await websocket.send(project_code)
    except websockets.ConnectionClosed:
        print("Connection closed")

start_server = websockets.serve(send_project, SERVER_HOST, SERVER_PORT)

asyncio.get_event_loop().run_until_complete(start_server)
print(f"WebSocket server listening on ws://{SERVER_HOST}:{SERVER_PORT}")
asyncio.get_event_loop().run_forever()