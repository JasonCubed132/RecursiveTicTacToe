import asyncio, json
from websockets.sync.client import connect

def hello():
    with connect("ws://localhost:1234") as websocket:
        turn = {
            "player": "X",
            "x": 2,
            "y": 1
        };
        websocket.send(json.dumps(turn))
        message = websocket.recv()
        print(f"Recieved: {message}")

hello()