"""
Security tests for Markitdown MCP Server

Tests cover:
- SSRF protection
- File size limits
- Base64 size limits
- Content-Type validation
- Error message sanitization
"""

import pytest
import base64
from src.mcp_server import validate_url_ssrf, convert_to_markdown


class TestSSRFProtection:
    """Test SSRF attack prevention."""

    @pytest.mark.asyncio
    async def test_block_localhost(self):
        """Should block requests to localhost."""
        with pytest.raises(ValueError, match="private IP"):
            validate_url_ssrf("http://localhost:8080/file.pdf")

    @pytest.mark.asyncio
    async def test_block_127_0_0_1(self):
        """Should block requests to 127.0.0.1."""
        with pytest.raises(ValueError, match="private IP"):
            validate_url_ssrf("http://127.0.0.1/file.pdf")

    @pytest.mark.asyncio
    async def test_block_aws_metadata(self):
        """Should block requests to AWS metadata endpoint."""
        with pytest.raises(ValueError, match="private IP"):
            validate_url_ssrf("http://169.254.169.254/latest/meta-data/")

    @pytest.mark.asyncio
    async def test_block_private_10(self):
        """Should block requests to 10.x.x.x private network."""
        with pytest.raises(ValueError, match="private IP"):
            validate_url_ssrf("http://10.0.0.1/file.pdf")

    @pytest.mark.asyncio
    async def test_block_private_192(self):
        """Should block requests to 192.168.x.x private network."""
        with pytest.raises(ValueError, match="private IP"):
            validate_url_ssrf("http://192.168.1.1/file.pdf")

    @pytest.mark.asyncio
    async def test_block_private_172(self):
        """Should block requests to 172.16-31.x.x private network."""
        with pytest.raises(ValueError, match="private IP"):
            validate_url_ssrf("http://172.16.0.1/file.pdf")

    @pytest.mark.asyncio
    async def test_block_file_scheme(self):
        """Should block file:// scheme."""
        with pytest.raises(ValueError, match="scheme not allowed"):
            validate_url_ssrf("file:///etc/passwd")

    @pytest.mark.asyncio
    async def test_block_ftp_scheme(self):
        """Should block ftp:// scheme."""
        with pytest.raises(ValueError, match="scheme not allowed"):
            validate_url_ssrf("ftp://example.com/file.pdf")

    @pytest.mark.asyncio
    async def test_allow_valid_http(self):
        """Should allow valid HTTP URLs."""
        # Should not raise
        try:
            validate_url_ssrf("http://example.com/file.pdf")
        except ValueError as e:
            # Only fail if it's not a DNS resolution error (example.com is valid)
            if "Cannot resolve" not in str(e):
                raise

    @pytest.mark.asyncio
    async def test_allow_valid_https(self):
        """Should allow valid HTTPS URLs."""
        try:
            validate_url_ssrf("https://example.com/file.pdf")
        except ValueError as e:
            if "Cannot resolve" not in str(e):
                raise


class TestFileSizeLimits:
    """Test file size limit enforcement."""

    @pytest.mark.asyncio
    async def test_base64_size_limit(self):
        """Should reject base64 input exceeding size limit."""
        # Create 101MB of data (exceeds 100MB limit)
        large_data = b'A' * (101 * 1024 * 1024)
        large_base64 = base64.b64encode(large_data).decode('ascii')

        with pytest.raises(ValueError, match="Base64 input size exceeds"):
            await convert_to_markdown({'fileBase64': large_base64})

    @pytest.mark.asyncio
    async def test_base64_accepts_small_files(self):
        """Should accept base64 input within size limit."""
        # Create 1MB of data (within limit)
        small_data = b'A' * (1 * 1024 * 1024)
        small_base64 = base64.b64encode(small_data).decode('ascii')

        # This will fail with invalid PDF error, but shouldn't hit size limit
        with pytest.raises(ValueError) as exc_info:
            await convert_to_markdown({'fileBase64': small_base64})

        # Ensure it's not a size limit error
        assert "size exceeds" not in str(exc_info.value).lower()


class TestInputValidation:
    """Test input validation."""

    @pytest.mark.asyncio
    async def test_require_input(self):
        """Should require either fileUrl or fileBase64."""
        with pytest.raises(ValueError, match="Either fileUrl or fileBase64 must be provided"):
            await convert_to_markdown({})

    @pytest.mark.asyncio
    async def test_invalid_base64(self):
        """Should reject invalid base64 encoding."""
        with pytest.raises(ValueError, match="Invalid base64"):
            await convert_to_markdown({'fileBase64': 'not-valid-base64!!!'})


class TestContentTypeValidation:
    """Test Content-Type validation (integration tests require real server)."""

    # Note: Full Content-Type validation tests require mocking httpx responses
    # These would be integration tests
    pass


class TestErrorHandling:
    """Test error message sanitization."""

    @pytest.mark.asyncio
    async def test_generic_error_messages(self):
        """Should return generic error messages to users."""
        # Test with invalid input that would cause internal error
        try:
            await convert_to_markdown({'fileBase64': 'invalid'})
        except ValueError as e:
            error_msg = str(e)
            # Should not expose internal paths or system details
            assert '/usr' not in error_msg.lower()
            assert '/home' not in error_msg.lower()
            assert 'traceback' not in error_msg.lower()


# Test runner
if __name__ == '__main__':
    pytest.main([__file__, '-v'])
