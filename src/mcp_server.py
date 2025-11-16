"""
MCP Server Implementation for Markitdown

This module implements the Model Context Protocol server that exposes
Markitdown document conversion as an MCP tool for AI agents.
"""

import os
import tempfile
import ipaddress
import socket
import secrets
import shutil
from typing import Any, Dict
from urllib.parse import urlparse
import httpx
from markitdown import MarkItDown
from apify import Actor
from mcp.server.fastmcp import FastMCP
from mcp.types import  Tool, TextContent


# Security Configuration
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB limit
MAX_BASE64_SIZE = 100 * 1024 * 1024  # 100MB base64 limit
DOWNLOAD_TIMEOUT = httpx.Timeout(60.0, connect=10.0)  # 60s total, 10s connect

# SSRF Protection: Blocked IP ranges
BLOCKED_IP_RANGES = [
    ipaddress.ip_network('127.0.0.0/8'),     # Loopback
    ipaddress.ip_network('10.0.0.0/8'),      # Private
    ipaddress.ip_network('172.16.0.0/12'),   # Private
    ipaddress.ip_network('192.168.0.0/16'),  # Private
    ipaddress.ip_network('169.254.0.0/16'),  # Link-local (AWS metadata)
    ipaddress.ip_network('::1/128'),         # IPv6 loopback
    ipaddress.ip_network('fc00::/7'),        # IPv6 private
    ipaddress.ip_network('fe80::/10'),       # IPv6 link-local
]

# SSRF Protection: Allowed URL schemes
ALLOWED_SCHEMES = ['http', 'https']

# Content-Type whitelist
ALLOWED_CONTENT_TYPES = {
    'application/pdf': '.pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
    'application/vnd.ms-excel': '.xls',
    'application/vnd.ms-powerpoint': '.ppt',
    'application/msword': '.doc',
    'image/png': '.png',
    'image/jpeg': '.jpg',
    'image/gif': '.gif',
    'image/webp': '.webp',
    'text/html': '.html',
    'text/plain': '.txt',
    'text/csv': '.csv',
    'application/zip': '.zip',
}


# Initialize Markitdown converter
md_converter = MarkItDown()


def validate_url_ssrf(url: str) -> None:
    """
    Validate URL to prevent SSRF attacks.

    Args:
        url: The URL to validate

    Raises:
        ValueError: If URL is invalid or points to blocked resource
    """
    parsed = urlparse(url)

    # Check scheme whitelist
    if parsed.scheme not in ALLOWED_SCHEMES:
        raise ValueError(f'URL scheme not allowed: {parsed.scheme}. Only http and https are supported.')

    if not parsed.hostname:
        raise ValueError('URL must contain a valid hostname')

    # Resolve hostname to IP address
    try:
        ip_str = socket.gethostbyname(parsed.hostname)
        ip_obj = ipaddress.ip_address(ip_str)

        # Check if IP is in blocked ranges
        for blocked_range in BLOCKED_IP_RANGES:
            if ip_obj in blocked_range:
                # Log security event
                Actor.log.warning(f'SSRF attempt blocked: {url} resolves to private IP {ip_str}')
                raise ValueError(
                    'Access to private IP addresses and cloud metadata endpoints is forbidden for security reasons.'
                )

    except socket.gaierror as e:
        raise ValueError(f'Cannot resolve hostname: {parsed.hostname}')
    except ValueError as e:
        # Re-raise validation errors
        raise


async def convert_to_markdown(arguments: Dict[str, Any]) -> str:
    """
    Convert a document to Markdown using Markitdown with security protections.

    Security features:
    - SSRF protection (blocks private IPs, metadata endpoints)
    - File size limits (100MB max)
    - Request timeouts (60s total, 10s connect)
    - Content-Type validation
    - Secure temp file handling

    Args:
        arguments: Dictionary containing either 'fileUrl' or 'fileBase64'

    Returns:
        Markdown text content

    Raises:
        ValueError: If validation fails or conversion errors occur
    """
    file_url = arguments.get('fileUrl')
    file_base64 = arguments.get('fileBase64')

    if not file_url and not file_base64:
        raise ValueError('Either fileUrl or fileBase64 must be provided')

    temp_dir = None

    try:
        # Case 1: Download file from URL
        if file_url:
            Actor.log.info(f'Downloading file from URL: {file_url}')

            # SECURITY: Validate URL to prevent SSRF attacks
            validate_url_ssrf(file_url)

            # Download file with streaming and size limits
            async with httpx.AsyncClient(timeout=DOWNLOAD_TIMEOUT) as client:
                async with client.stream('GET', file_url, follow_redirects=True) as response:
                    response.raise_for_status()

                    # SECURITY: Validate Content-Type
                    content_type = response.headers.get('content-type', '').split(';')[0].strip().lower()
                    if content_type and content_type not in ALLOWED_CONTENT_TYPES:
                        await Actor.push_data({
                            'event': 'security_blocked_content_type',
                            'url': file_url,
                            'content_type': content_type,
                        })
                        raise ValueError(
                            f'Unsupported content type: {content_type}. '
                            f'Supported types: {", ".join(list(ALLOWED_CONTENT_TYPES.keys())[:5])}...'
                        )

                    # Determine file extension from Content-Type
                    file_ext = ALLOWED_CONTENT_TYPES.get(content_type, '.pdf')

                    # SECURITY: Stream download with size limit
                    file_content = bytearray()
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        file_content.extend(chunk)
                        if len(file_content) > MAX_FILE_SIZE:
                            await Actor.push_data({
                                'event': 'security_blocked_file_size',
                                'url': file_url,
                                'size_attempted': len(file_content),
                                'max_size': MAX_FILE_SIZE,
                            })
                            raise ValueError(
                                f'File size exceeds maximum allowed size of {MAX_FILE_SIZE // (1024*1024)}MB'
                            )

                    file_content = bytes(file_content)
                    Actor.log.info(f'Downloaded {len(file_content)} bytes from URL')

        # Case 2: Decode base64 file
        else:
            import base64
            Actor.log.info('Decoding base64-encoded file')

            # SECURITY: Validate base64 size before decoding
            if len(file_base64) > MAX_BASE64_SIZE:
                await Actor.push_data({
                    'event': 'security_blocked_base64_size',
                    'size_attempted': len(file_base64),
                    'max_size': MAX_BASE64_SIZE,
                })
                raise ValueError(
                    f'Base64 input size exceeds maximum allowed size of {MAX_BASE64_SIZE // (1024*1024)}MB'
                )

            try:
                file_content = base64.b64decode(file_base64, validate=True)
            except Exception as e:
                raise ValueError(f'Invalid base64 encoding: {str(e)}')

            # Default extension (should be provided by user in future enhancement)
            file_ext = '.pdf'

        # SECURITY: Create secure temporary directory
        temp_dir = tempfile.mkdtemp(prefix='markitdown_secure_')
        temp_filename = f"{secrets.token_hex(16)}{file_ext}"
        tmp_file_path = os.path.join(temp_dir, temp_filename)

        # Write file to secure temp location
        with open(tmp_file_path, 'wb') as f:
            f.write(file_content)

        # Convert to Markdown
        Actor.log.info(f'Converting file to Markdown (size: {len(file_content)} bytes, type: {file_ext})')
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

    except httpx.TimeoutException:
        error_msg = 'Request timeout: File download took too long'
        Actor.log.error(error_msg)
        await Actor.push_data({
            'event': 'conversion_error',
            'error': 'timeout',
            'file_url': file_url if file_url else None,
        })
        raise ValueError('Request timeout. Please try with a smaller file or faster server.')

    except httpx.HTTPStatusError as e:
        error_msg = f'HTTP {e.response.status_code}'
        Actor.log.error(f'Failed to download file: {error_msg}')
        await Actor.push_data({
            'event': 'conversion_error',
            'error': f'http_error_{e.response.status_code}',
            'file_url': file_url,
        })
        raise ValueError(f'Failed to download file: {error_msg}')

    except ValueError as e:
        # Re-raise validation errors (already logged above)
        raise

    except Exception as e:
        # Log detailed error for debugging
        Actor.log.error(f'Conversion error: {type(e).__name__}: {str(e)}')
        await Actor.push_data({
            'event': 'conversion_error',
            'error_type': type(e).__name__,
        })
        # Generic user-facing error message
        raise ValueError(
            'Document conversion failed. Please verify the file format is supported and try again.'
        )

    finally:
        # SECURITY: Clean up temporary directory
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                Actor.log.warning(f'Failed to clean up temp directory: {str(e)}')


async def start_mcp_server(port: int = 3001):
    """
    Start the MCP server with Markitdown tools using HTTP transport.

    Security features:
    - HTTP security headers (X-Content-Type-Options, X-Frame-Options, etc.)
    - SSRF protection
    - File size limits
    - Request timeouts

    Args:
        port: Port number for the HTTP server
    """
    # Create FastMCP server instance with HTTP configuration
    mcp = FastMCP(
        name="Markitdown MCP Server",
        host="0.0.0.0",  # Listen on all interfaces
        port=port,
        streamable_http_path="/mcp"  # MCP endpoint path
    )

    # SECURITY: Add HTTP security headers middleware
    @mcp.app.middleware("http")
    async def add_security_headers(request, call_next):
        """Add security headers to all HTTP responses."""
        response = await call_next(request)

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # Enable XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Strict transport security (HTTPS only in production)
        # Commented out as MCP servers typically run behind reverse proxy
        # response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Content Security Policy
        response.headers["Content-Security-Policy"] = "default-src 'self'"

        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions policy
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        return response

    # Register the convert_to_markdown tool
    @mcp.tool()
    async def convert_to_markdown_tool(file_url: str = None, file_base64: str = None) -> str:
        """
        Convert documents (PDF, DOCX, PPTX, XLSX, images, etc.) to clean Markdown.
        Supports 29+ file formats. Ideal for RAG pipelines, knowledge bases, and AI workflows.

        Security features:
        - SSRF protection (blocks private IPs, cloud metadata endpoints)
        - File size limits (100MB max)
        - Request timeouts (60s max)
        - Content-Type validation

        Args:
            file_url: URL of the document to convert
            file_base64: Base64-encoded file content (alternative to URL)

        Returns:
            Clean Markdown text
        """
        arguments = {}
        if file_url:
            arguments['fileUrl'] = file_url
        if file_base64:
            arguments['fileBase64'] = file_base64

        return await convert_to_markdown(arguments)

    Actor.log.info('MCP Server initialized with convert_to_markdown tool')
    Actor.log.info('Security features enabled: SSRF protection, file size limits, timeouts, security headers')

    # Run HTTP MCP server using streamable HTTP transport
    Actor.log.info(f'Starting HTTP MCP server on port {port}...')

    # Run the streamable HTTP server (host and port configured in __init__)
    await mcp.run_streamable_http_async()
