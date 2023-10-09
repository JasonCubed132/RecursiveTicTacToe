import asyncio
from websockets.sync.client import connect

def hello():
    with connect("ws://localhost:1234") as websocket:
        websocket.send("Hello world!")
        message = websocket.recv()
        print(f"Recieved: {message}")

hello()