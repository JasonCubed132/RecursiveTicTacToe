import asyncio, json
from websockets.sync.client import connect

def hello():
    with connect("ws://localhost:1234") as websocket:
        turn = {
            "action": "turn",
            "payload": {
                "player": "X",
                "x": 2,
                "y": 1
            }
        };
        websocket.send(json.dumps(turn))
        message = websocket.recv()
        print(f"Recieved: {message}")

        get_state = {
            "action": "get_board"
        }
        websocket.send(json.dumps(get_state))
        message = websocket.recv()
        print(f"Recieved: {message}")

        get_state = {
            "action": "get_winner"
        }
        websocket.send(json.dumps(get_state))
        message = websocket.recv()
        print(f"Recieved: {message}")

hello()