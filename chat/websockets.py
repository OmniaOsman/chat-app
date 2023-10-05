import asyncio
import websockets

async def hello():
    loop = asyncio.get_running_loop()
    try:
        async with websockets.connect('ws://localhost:8000/ws/chat/OmniaOsman/os/?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjk2NTA4MTAyLCJpYXQiOjE2OTY1MDc4MDIsImp0aSI6ImJhZjRhMWFhYjAzZjQxMzE4ODE2MGNmMTFmNzJjYjIzIiwidXNlcl9pZCI6MTZ9.Fc8qhMcfhqzMLiWU4Qdf5e2WEvcmhJCwlJZ_0M6XSq4') as websocket:
            await websocket.send('Hello')
            response = await websocket.recv()
            print(f'Received: {response}')
    except Exception as e:
        print(f'Error: {e}')

asyncio.run(hello())
