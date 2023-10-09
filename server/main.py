import asyncio
from websockets.server import serve
from typing import Union

class Cell():
    def __init__(self) -> Cell:
        self.state = ""

    def set(self, val: str) -> bool:
        if self.state == "":
            self.state = val
            return True
        return False

    def get(self) -> str:
        return self.state
    
    def __str__(self) -> str:
        return self.state


class Board():
    def __init__(self, size: int = 3) -> Board:
        self.size = size
        self.cells = []
        for i in range(0, size):
            row = []
            for j in range(0, size):
                row.append(Cell())

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
        return ("-"*length).join(lines)

    def getWinner(self) -> Union[str, None]:
        if self.size == 0:
            # Nothing to evaluate
            return None
        
        # Evaluate each row
        for i in self.size:
            

async def echo(websocket):
    async for message in websocket:
        print(f"Echoing: {message}")
        await websocket.send(message)

async def main():
    async with serve(echo, "localhost", 1234):
        await asyncio.Future()

asyncio.run(main())