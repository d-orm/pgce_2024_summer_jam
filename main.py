# /// script
# dependencies = [
#   "pygame-ce",
# ]
# ///

import asyncio

from src.app import App


if __name__ == "__main__":
    app = App()
    asyncio.run(app.run())
