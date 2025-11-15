"""
Entrypoint for Apify CLI - imports and runs the main Actor code.
"""
from src.main import main
import asyncio

if __name__ == '__main__':
    asyncio.run(main())
