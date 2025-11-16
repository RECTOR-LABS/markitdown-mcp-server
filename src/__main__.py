"""
Module entry point for Apify CLI.

The Apify CLI runs Python actors with: python -m src
This file makes the src directory executable as a module.
"""
from src.main import main
import asyncio

if __name__ == '__main__':
    asyncio.run(main())
