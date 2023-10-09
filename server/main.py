import asyncio, json
from websockets.server import serve
from typing import Union, List

class Cell():
    def __init__(self):
        self.state: Union[str, None] = None

    def set(self, val: str) -> bool:
        if self.state == None:
            if len(val) != 1:
                raise ValueError(f"value {val} is longer than 1")

            self.state = val
            return True
        return False

    def get(self) -> Union[str, None]:
        return self.state
    
    def __str__(self) -> str:
        if self.state == None:
            return " "
        return self.state


class Board():
    def __init__(self, size: int = 3):
        self.size = size
        self.cells = []
        for _ in range(0, size):
            row = []
            for _ in range(0, size):
                row.append(Cell())
            self.cells.append(row)

    def setCell(self, x: int, y: int, player: str) -> bool:
        if x < 0 or x >= self.size:
            return False
        if y < 0 or y >= self.size:
            return False
        return self.cells[y][x].set(player)

    def __str__(self) -> str:
        lines = []
        for row in self.cells:
            lines.append("|".join([str(cell) for cell in row]))

        length = max([len(line) for line in lines])
        filler = "-"*length + "\n"

        appended_lines = [line + "\n" for line in lines]
        output_lines = filler.join(appended_lines)

        return output_lines
    
    def toArray(self) -> List[Union[str, None]]:
        output_array = []
        for i in range(self.size):
            output_row = []
            for j in range(self.size):
                cell = self.cells[i][j].get()
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
        
        # Evaluate each row
        for i in range(self.size):
            result = self.getWinnerFromArray(self.cells[i])
            if result != None:
                return result

        # Evaluate each column
        for i in range(self.size):
            column = [self.cells[j][i] for j in range(self.size)]
            result = self.getWinnerFromArray(column)
            if result != None:
                return result

        leading = [self.cells[i][i] for i in range(self.size)]
        result = self.getWinnerFromArray(leading)
        if result != None:
            return result
        
        trailing = [self.cells[self.size-1-i][i] for i in range(self.size)]
        result = self.getWinnerFromArray(trailing)
        if result != None:
            return result
        
        return None

game: Board = None

async def handleGameConnection(websocket):
    global game
    print("Game connected")
    async for message in websocket:
        parsed_message = json.loads(message)

        action = parsed_message["action"]
        if action == "turn":
            payload = parsed_message["payload"]

            x = int(payload["x"])
            y = int(payload["y"])
            player = payload["player"]

            accepted = game.setCell(x, y, player)
            await websocket.send(json.dumps(accepted))

        elif action == "get_board":
            game_state = game.toArray()
            await websocket.send(json.dumps(game_state))

        elif action == "get_winner":
            winner = game.getWinner()
            await websocket.send(json.dumps(winner))

async def main():
    global game
    game = Board()

    async with serve(handleGameConnection, "localhost", 1234):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
