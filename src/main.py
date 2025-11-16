"""
Markitdown MCP Server - Main Entry Point

This Actor provides a cloud-hosted MCP (Model Context Protocol) server
that wraps Microsoft's Markitdown library for converting documents to Markdown.

Features:
- Convert 29+ file formats to clean, AI-ready Markdown
- Zero Python dependency for end users (cloud-hosted)
- Pay-per-event billing model
- MCP-native for AI agent discovery
- Smart standby mode auto-detection for local development
"""

import asyncio
import os
from apify import Actor
from src.mcp_server import start_mcp_server


def is_running_locally() -> bool:
    """
    Detect if Actor is running in local development environment.

    Uses multiple detection methods for reliability:
    1. APIFY_IS_AT_HOME - Set to '1' on Apify Cloud, not set locally
    2. APIFY_ACTOR_ID - Cloud always assigns an Actor ID
    3. APIFY_DEFAULT_KEY_VALUE_STORE_ID - Cloud storage vs local storage

    Returns:
        True if running locally, False if running on Apify Cloud
    """
    # Method 1: Check for Apify Cloud environment variable (most reliable)
    is_at_home = os.getenv('APIFY_IS_AT_HOME')
    if is_at_home is None:
        return True  # Not on Apify Cloud

    # Method 2: Check for Actor ID (Cloud always assigns one)
    actor_id = os.getenv('APIFY_ACTOR_ID')
    if actor_id is None:
        return True  # No Actor ID = local development

    # Method 3: Check for Cloud storage (additional verification)
    default_kv_store = os.getenv('APIFY_DEFAULT_KEY_VALUE_STORE_ID')
    if default_kv_store is None:
        return True  # Local storage structure

    return False  # Running on Apify Cloud


async def main():
    """
    Main entry point for the Markitdown MCP Server Actor.

    This function:
    1. Initializes the Apify Actor environment
    2. Charges for Actor start event
    3. Smart standby mode detection (auto-enable for local development)
    4. Verifies standby mode (required for MCP servers on Cloud)
    5. Starts the MCP server
    """
    async with Actor:
        # Charge for Actor start
        await Actor.charge(event_name='actor-start')

        # Smart standby mode detection
        explicit_standby = os.getenv('APIFY_META_ORIGIN') == 'STANDBY'
        is_local = is_running_locally()
        server_port = int(os.getenv('ACTOR_WEB_SERVER_PORT', '3001'))

        # Auto-enable standby mode for local development
        if is_local and not explicit_standby:
            Actor.log.info('🔧 Local development detected - auto-enabling standby mode')
            Actor.log.info(f'💡 Tip: On Apify Cloud, standby mode is configured via actor.json')
            standby_mode = True
        else:
            standby_mode = explicit_standby

        # Safety check: Fail if running on Cloud without standby mode
        if not standby_mode and not is_local:
            error_msg = (
                'This Actor must run in standby mode on Apify Cloud. '
                'Please enable standby mode in Actor settings or set usesStandbyMode: true in actor.json'
            )
            Actor.log.error(error_msg)
            await Actor.exit(status_message=error_msg)
            return

        Actor.log.info(f'Starting Markitdown MCP Server on port {server_port}...')

        # Start the MCP server
        await start_mcp_server(port=server_port)


if __name__ == '__main__':
    asyncio.run(main())
