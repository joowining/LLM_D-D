import random
import math
from langchain_core import tools

@tools.tool
def rolling_dice() -> int :
    return math.floor(20*random.random()) + 1


if __name__ == "__main__":
    for i in range(1,20):
        print(rolling_dice())
