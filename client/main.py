import asyncio, json
from websockets.sync.client import connect

def main():
    with connect("ws://localhost:1234") as websocket:
        session_id = None
        while True:
            line = input("> ")

            if len(line) == 0:
                print("No data entered")
                continue

            data = line.split(" ")

            action = data[0]

            if action == "new_session":
                websocket.send(json.dumps({"action": "new_session"}))
                message = websocket.recv()
                session_id = json.loads(message)["session_id"]
                print(session_id)

            elif action == "connect_session":
                tmp_session_id = int(data[1])
                websocket.send(json.dumps({"action": "connect_session", "session_id": tmp_session_id}))
                reply = json.loads(websocket.recv())
                if reply["accepted"]:
                    session_id = tmp_session_id
                else:
                    print(reply["reason"])

            if action == "turn":
                x = int(data[1])
                y = int(data[2])
                player = data[3]

                turn = {
                    "action": "turn",
                    "payload": {
                        "player": player,
                        "x": x,
                        "y": y
                    }
                };
                websocket.send(json.dumps(turn))
                message = websocket.recv()
                print(f"Recieved: {message}")

            elif action == "board":
                get_state = {
                    "action": "get_board"
                }
                websocket.send(json.dumps(get_state))
                message = websocket.recv()
                print(f"Recieved: {message}")

            elif action == "winner":
                get_state = {
                    "action": "get_winner"
                }
                websocket.send(json.dumps(get_state))
                message = websocket.recv()
                print(f"Recieved: {message}")

            elif action == "exit":
                break

if __name__ == "__main__":
    main()
