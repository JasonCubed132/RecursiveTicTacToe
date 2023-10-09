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
        for i in range(0, size):
            row = []
            for j in range(0, size):
                row.append(Cell())
            self.cells.append(row)
        print(self)

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
    
    def to_dict(self) -> dict:
        output = {}

        output_array = []
        for i in range(self.size):
            output_row = []
            for j in range(self.size):
                cell = self.cells[i][j].get()
                output_row.append(cell)

            output_array.append(output_row)
        
        output["board"] = output_array
        return output

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
        for i in self.size:
            result = self.getWinnerFromArray(self.cells[i])
            if result != None:
                return result

        # Evaluate each column
        for i in self.size:
            column = [self.cells[j][i] for j in self.size]
            result = self.getWinnerFromArray(column)
            if result != None:
                return result

        leading = [self.cells[i][i] for i in self.size]
        result = self.getWinnerFromArray(leading)
        if result != None:
            return result
        
        trailing = [self.cells[3-i][i] for i in self.size]
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
        x = int(parsed_message["x"])
        y = int(parsed_message["y"])
        player = parsed_message["player"]
        accepted = game.setCell(x, y, player)
        game_state = game.to_dict()
        if accepted:
            print(f"Set cell {x} {y} to {player}")
            game_state["accepted"] = True
            await websocket.send(json.dumps(game_state))
        else:
            print(f"Failed to set cell {x} {y} to {player}")
            game_state["accepted"] = False
            await websocket.send(json.dumps(game_state))
       

async def main():
    global game
    game = Board()

    async with serve(handleGameConnection, "localhost", 1234):
        await asyncio.Future()

asyncio.run(main())