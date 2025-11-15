"""
MCP Server Implementation for Markitdown

This module implements the Model Context Protocol server that exposes
Markitdown document conversion as an MCP tool for AI agents.
"""

import os
import tempfile
from typing import Any, Dict
from urllib.parse import urlparse
import httpx
from markitdown import MarkItDown
from apify import Actor
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


# Initialize Markitdown converter
md_converter = MarkItDown()


async def convert_to_markdown(arguments: Dict[str, Any]) -> str:
    """
    Convert a document to Markdown using Markitdown.

    Args:
        arguments: Dictionary containing either 'fileUrl' or 'fileBase64'

    Returns:
        Markdown text content

    Raises:
        ValueError: If neither fileUrl nor fileBase64 is provided
    """
    file_url = arguments.get('fileUrl')
    file_base64 = arguments.get('fileBase64')

    if not file_url and not file_base64:
        raise ValueError('Either fileUrl or fileBase64 must be provided')

    try:
        # Case 1: Download file from URL
        if file_url:
            Actor.log.info(f'Downloading file from URL: {file_url}')

            # Validate URL
            parsed_url = urlparse(file_url)
            if not parsed_url.scheme or not parsed_url.netloc:
                raise ValueError(f'Invalid URL: {file_url}')

            # Download file
            async with httpx.AsyncClient() as client:
                response = await client.get(file_url, follow_redirects=True)
                response.raise_for_status()
                file_content = response.content

            # Determine file extension from URL or Content-Type
            file_ext = os.path.splitext(parsed_url.path)[1] or '.pdf'

        # Case 2: Decode base64 file
        else:
            import base64
            Actor.log.info('Decoding base64-encoded file')
            file_content = base64.b64decode(file_base64)
            file_ext = '.pdf'  # Default, should be specified in arguments

        # Save to temporary file for Markitdown processing
        with tempfile.NamedTemporaryFile(suffix=file_ext, delete=False) as tmp_file:
            tmp_file.write(file_content)
            tmp_file_path = tmp_file.name

        try:
            # Convert to Markdown
            Actor.log.info(f'Converting file to Markdown (size: {len(file_content)} bytes)')
            result = md_converter.convert(tmp_file_path)
            markdown_text = result.text_content

            # Log conversion success
            await Actor.push_data({
                'event': 'conversion_success',
                'file_size': len(file_content),
                'markdown_length': len(markdown_text),
                'file_type': file_ext,
            })

            # Charge for document conversion
            await Actor.charge(event_name='document-conversion')

            Actor.log.info(f'Conversion successful! Markdown length: {len(markdown_text)} chars')
            return markdown_text

        finally:
            # Clean up temporary file
            if os.path.exists(tmp_file_path):
                os.unlink(tmp_file_path)

    except httpx.HTTPStatusError as e:
        error_msg = f'Failed to download file: HTTP {e.response.status_code}'
        Actor.log.error(error_msg)
        await Actor.push_data({
            'event': 'conversion_error',
            'error': error_msg,
            'file_url': file_url,
        })
        raise ValueError(error_msg)

    except Exception as e:
        error_msg = f'Conversion failed: {str(e)}'
        Actor.log.error(error_msg)
        await Actor.push_data({
            'event': 'conversion_error',
            'error': error_msg,
        })
        raise


async def start_mcp_server(port: int = 3001):
    """
    Start the MCP server with Markitdown tools.

    Args:
        port: Port number for the server
    """
    # Create MCP server instance
    server = Server("markitdown-mcp-server")

    # Register the convert_to_markdown tool
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="convert_to_markdown",
                description=(
                    "Convert documents (PDF, DOCX, PPTX, XLSX, images, etc.) to clean Markdown. "
                    "Supports 29+ file formats. Ideal for RAG pipelines, knowledge bases, and AI workflows."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "fileUrl": {
                            "type": "string",
                            "description": "URL of the document to convert",
                        },
                        "fileBase64": {
                            "type": "string",
                            "description": "Base64-encoded file content (alternative to fileUrl)",
                        },
                    },
                    "oneOf": [
                        {"required": ["fileUrl"]},
                        {"required": ["fileBase64"]},
                    ],
                },
            )
        ]

    # Register tool handler
    @server.call_tool()
    async def call_tool(name: str, arguments: Any) -> list[TextContent]:
        if name == "convert_to_markdown":
            markdown = await convert_to_markdown(arguments)
            return [TextContent(type="text", text=markdown)]
        else:
            raise ValueError(f"Unknown tool: {name}")

    # Start server using stdio transport
    Actor.log.info('MCP Server initialized with convert_to_markdown tool')

    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())
