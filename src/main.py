"""
Markitdown MCP Server - Main Entry Point

This Actor provides a cloud-hosted MCP (Model Context Protocol) server
that wraps Microsoft's Markitdown library for converting documents to Markdown.

Features:
- Convert 29+ file formats to clean, AI-ready Markdown
- Zero Python dependency for end users (cloud-hosted)
- Pay-per-event billing model
- MCP-native for AI agent discovery
"""

import asyncio
import os
from apify import Actor
from mcp_server import start_mcp_server


async def main():
    """
    Main entry point for the Markitdown MCP Server Actor.

    This function:
    1. Initializes the Apify Actor environment
    2. Charges for Actor start event
    3. Verifies standby mode (required for MCP servers)
    4. Starts the MCP server
    """
    async with Actor:
        # Charge for Actor start
        await Actor.charge(event_name='actor-start')

        # Check if running in standby mode
        standby_mode = os.getenv('APIFY_META_ORIGIN') == 'STANDBY'
        server_port = int(os.getenv('ACTOR_WEB_SERVER_PORT', '3001'))

        if not standby_mode:
            error_msg = 'This Actor must run in standby mode. Please enable standby mode in Actor settings.'
            Actor.log.error(error_msg)
            await Actor.exit(status_message=error_msg)
            return

        Actor.log.info(f'Starting Markitdown MCP Server on port {server_port}...')

        # Start the MCP server
        await start_mcp_server(port=server_port)


if __name__ == '__main__':
    asyncio.run(main())
