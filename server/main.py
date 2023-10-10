import asyncio, json, random
from websockets.server import serve
from typing import Union, List

class AbstractCell():
    def __init__(self, depth: int = 1, size: int = 1):
        self.size: int = size
        self.winner: Union[str, None] = None

    def __eq__(self, other) -> bool:
        if other == None:
            return False
        return self.winner == other.getWinner()

    def getWinner(self) -> Union[str, None]:
        return self.winner

    def setCell(self, x: int, y: int, player: str) -> bool:
        return False
    
    def toArray(self):
        return self.winner

class Cell(AbstractCell):
    def __init__(self):
        super().__init__()

    def __str__(self) -> str:
        if self.winner == None:
            return " "
        return self.winner

    def setCell(self, x: int, y: int, player: str) -> bool:
        if self.winner == None:
            if len(player) != 1:
                raise ValueError(f"value {player} is longer than 1")

            self.winner = player
            return True
        return False

class Board(AbstractCell):
    def __init__(self, depth: int = 2, size: int = 3):
        super().__init__(depth, size)

        self.cells: List[List[AbstractCell]] = []
        for _ in range(0, size):
            row = []
            for _ in range(0, size):
                if depth <= 1:
                    row.append(Cell())
                else:
                    row.append(Board(depth - 1, size))
            self.cells.append(row)

    def __str__(self) -> str:
        lines = []
        for row in self.cells:
            line = []
            for cell in row:
                cell_str = str(cell).split("\n")
                line.append(cell_str)

            transposed_line = zip(*line)

            concated_line = ["|".join(individual_line) for individual_line in transposed_line]

            lines.append(concated_line)

        length = max([len(line) for line in lines])
        filler = "-"*length + "\n"

        appended_lines = [line + "\n" for line in lines]
        output_lines = filler.join(appended_lines)

        return output_lines

    def setCell(self, x: int, y: int, player: str) -> bool:
        if self.winner == None:
            if x < 0 or x >= self.size:
                return False
            if y < 0 or y >= self.size:
                return False

            return self.cells[y][x].setCell(x, y, player)
        return False

    def toArray(self):
        output_array = []
        for i in range(self.size):
            output_row = []
            for j in range(self.size):
                cell = self.cells[i][j].toArray()
                output_row.append(cell)

            output_array.append(output_row)

        return output_array

    def isAllElementsIdentical(self, array: List[str]) -> bool:
        if len(array) == 0:
            return False

        value = array[0]
        for i in range(len(array)):
            if array[i] != value:
                return False

        return True
    
    def getWinnerFromArray(self, array: List[str]) -> Union[str, None]:
        if not self.isAllElementsIdentical(array):
            return None
        return array[0]

    def getWinner(self) -> Union[str, None]:
        if self.size == 0:
            # Nothing to evaluate
            return None

        if self.winner != None:
            return self.winner

        # Evaluate each row
        for i in range(self.size):
            result = self.getWinnerFromArray(self.cells[i])
            if result != None:
                self.winner = result.getWinner()
                return self.winner

        # Evaluate each column
        for i in range(self.size):
            column = [self.cells[j][i] for j in range(self.size)]
            result = self.getWinnerFromArray(column)
            if result != None:
                self.winner = result.getWinner()
                return self.winner

        # Evaluate leading diagonal
        leading = [self.cells[i][i] for i in range(self.size)]
        result = self.getWinnerFromArray(leading)
        if result != None:
            self.winner = result.getWinner()
            return self.winner
        
        # Evaluate trailing diagonal
        trailing = [self.cells[self.size-1-i][i] for i in range(self.size)]
        result = self.getWinnerFromArray(trailing)
        if result != None:
            self.winner = result.getWinner()
            return self.winner

        return None

sessions = {}

async def handleGameConnection(websocket):
    global sessions
    current_session_id = None
    game = None
    print("Game connected")
    async for message in websocket:
        parsed_message = json.loads(message)
        action = parsed_message["action"]

        if current_session_id != None:
            game = sessions[current_session_id]

        if action == "new_session":
            new_session_id = random.randint(1, 100000000)
            while new_session_id in sessions:
                new_session_id = random.randint(1, 100000000)

            current_session_id = new_session_id

            sessions[new_session_id] = Board()

            await websocket.send(json.dumps({"session_id": new_session_id}))
            continue

        elif action == "connect_session":
            session_id = parsed_message["session_id"]

            if session_id in sessions:
                current_session_id = session_id
                await websocket.send(json.dumps({"accepted": True}))
                continue
            else:
                await websocket.send(json.dumps({"accepted": False, "reason": "Unable to find session"}))
                continue

        elif action == "turn":
            if game.getWinner() != None:
                await websocket.send(json.dumps({"accepted": False, "reason": "Already won"}))
                continue

            payload = parsed_message["payload"]

            x = int(payload["x"])
            y = int(payload["y"])
            player = payload["player"]

            accepted = game.setCell(x, y, player)

            if accepted:
                await websocket.send(json.dumps({"accepted": True,  "reason": ""}))
            else:
                await websocket.send(json.dumps({"accepted": False, "reason": "Parameter error"}))
            continue

        elif action == "get_board":
            game_state = game.toArray()
            await websocket.send(json.dumps(game_state))
            continue

        elif action == "get_winner":
            winner = game.getWinner()
            await websocket.send(json.dumps(winner))
            continue

async def main():
    async with serve(handleGameConnection, "localhost", 1234):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
