#!/usr/bin/env python3
"""
Tests for Pattern MCP Server
"""

import json
import os
import sys
from pathlib import Path

import pytest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.types import TextContent

from pattern_mcp_server import PatternServer


@pytest.fixture
def pattern_server():
    """Create a PatternServer instance for testing"""
    server = PatternServer()
    return server


@pytest.fixture
def mock_patterns_dir(tmp_path):
    """Create a mock patterns directory structure"""
    # Create fabric patterns
    fabric_dir = tmp_path / ".config" / "fabric" / "patterns"
    fabric_dir.mkdir(parents=True)

    # Create test pattern
    test_pattern = fabric_dir / "test_pattern"
    test_pattern.mkdir()
    (test_pattern / "system.md").write_text("System prompt content")
    (test_pattern / "user.md").write_text("User prompt content")

    # Create custom patterns
    custom_dir = tmp_path / ".config" / "custom_patterns"
    custom_dir.mkdir(parents=True)

    (custom_dir / "custom_test.md").write_text("Custom pattern content")
    (custom_dir / "custom_test.json").write_text(
        json.dumps(
            {
                "description": "Test custom pattern",
                "tags": ["test", "custom"],
                "author": "Test Author",
            }
        )
    )

    return tmp_path


class TestPatternServer:
    """Test cases for PatternServer class"""

    @pytest.mark.asyncio
    async def test_init(self, pattern_server):
        """Test PatternServer initialization"""
        assert pattern_server.server is not None
        assert pattern_server.fabric_patterns_dir.name == "patterns"
        assert pattern_server.custom_patterns_dir.name == "custom_patterns"
        assert isinstance(pattern_server.patterns_cache, dict)

    @pytest.mark.asyncio
    async def test_load_patterns(self, pattern_server, mock_patterns_dir, monkeypatch):
        """Test loading patterns from directories"""
        # Patch home directory
        monkeypatch.setattr(Path, "home", lambda: mock_patterns_dir)

        # Reinitialize with mocked paths
        pattern_server.fabric_patterns_dir = (
            mock_patterns_dir / ".config" / "fabric" / "patterns"
        )
        pattern_server.custom_patterns_dir = (
            mock_patterns_dir / ".config" / "custom_patterns"
        )

        await pattern_server.load_patterns()

        assert len(pattern_server.patterns_cache) == 2
        assert "test_pattern" in pattern_server.patterns_cache
        assert "custom_test" in pattern_server.patterns_cache

        # Check fabric pattern
        fabric_pattern = pattern_server.patterns_cache["test_pattern"]
        assert fabric_pattern["source"] == "fabric"
        assert fabric_pattern["system"] == "System prompt content"
        assert fabric_pattern["user"] == "User prompt content"

        # Check custom pattern
        custom_pattern = pattern_server.patterns_cache["custom_test"]
        assert custom_pattern["source"] == "custom"
        assert custom_pattern["content"] == "Custom pattern content"
        assert custom_pattern["metadata"]["description"] == "Test custom pattern"

    @pytest.mark.asyncio
    async def test_list_patterns(self, pattern_server, mock_patterns_dir, monkeypatch):
        """Test listing patterns with filters"""
        monkeypatch.setattr(Path, "home", lambda: mock_patterns_dir)
        pattern_server.fabric_patterns_dir = (
            mock_patterns_dir / ".config" / "fabric" / "patterns"
        )
        pattern_server.custom_patterns_dir = (
            mock_patterns_dir / ".config" / "custom_patterns"
        )

        # Test listing all patterns
        result = await pattern_server.list_patterns()
        assert isinstance(result, TextContent)
        data = json.loads(result.text)
        assert data["total"] == 2

        # Test filtering by source
        result = await pattern_server.list_patterns(source="fabric")
        data = json.loads(result.text)
        assert data["total"] == 1
        assert data["patterns"][0]["source"] == "fabric"

        # Test filtering by tags - note that fabric patterns don't have tags
        result = await pattern_server.list_patterns(tags=["custom"])
        data = json.loads(result.text)
        assert data["total"] == 1  # Only custom_test should match
        assert data["patterns"][0]["name"] == "custom_test"

    @pytest.mark.asyncio
    async def test_get_pattern(self, pattern_server, mock_patterns_dir, monkeypatch):
        """Test retrieving a specific pattern"""
        monkeypatch.setattr(Path, "home", lambda: mock_patterns_dir)
        pattern_server.fabric_patterns_dir = (
            mock_patterns_dir / ".config" / "fabric" / "patterns"
        )
        pattern_server.custom_patterns_dir = (
            mock_patterns_dir / ".config" / "custom_patterns"
        )

        # Get fabric pattern
        result = await pattern_server.get_pattern("test_pattern")
        assert isinstance(result, TextContent)
        data = json.loads(result.text)
        assert data["name"] == "test_pattern"
        assert data["source"] == "fabric"
        assert "System Prompt" in data["content"]
        assert "User Prompt" in data["content"]

        # Get custom pattern
        result = await pattern_server.get_pattern("custom_test")
        data = json.loads(result.text)
        assert data["name"] == "custom_test"
        assert data["source"] == "custom"
        assert data["content"] == "Custom pattern content"

        # Get non-existent pattern
        result = await pattern_server.get_pattern("non_existent")
        data = json.loads(result.text)
        assert "error" in data

    @pytest.mark.asyncio
    async def test_search_patterns(
        self, pattern_server, mock_patterns_dir, monkeypatch
    ):
        """Test searching patterns"""
        monkeypatch.setattr(Path, "home", lambda: mock_patterns_dir)
        pattern_server.fabric_patterns_dir = (
            mock_patterns_dir / ".config" / "fabric" / "patterns"
        )
        pattern_server.custom_patterns_dir = (
            mock_patterns_dir / ".config" / "custom_patterns"
        )

        # Search by content
        result = await pattern_server.search_patterns("custom")
        assert isinstance(result, TextContent)
        data = json.loads(result.text)
        assert len(data["results"]) > 0

        # Search with limit
        result = await pattern_server.search_patterns("test", limit=1)
        data = json.loads(result.text)
        assert len(data["results"]) == 1

    @pytest.mark.asyncio
    async def test_create_pattern(self, pattern_server, tmp_path, monkeypatch):
        """Test creating a new custom pattern"""
        custom_dir = tmp_path / ".config" / "custom_patterns"
        custom_dir.mkdir(parents=True)

        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        pattern_server.custom_patterns_dir = custom_dir

        # Create new pattern
        result = await pattern_server.create_pattern(
            "new_pattern",
            "This is a new pattern",
            {"description": "Test pattern", "tags": ["new"]},
        )

        assert isinstance(result, TextContent)
        data = json.loads(result.text)
        assert "message" in data
        assert "created successfully" in data["message"]

        # Verify files were created
        assert (custom_dir / "new_pattern.md").exists()
        assert (custom_dir / "new_pattern.json").exists()

        # Try to create duplicate
        result = await pattern_server.create_pattern(
            "new_pattern", "Duplicate content", {}
        )
        data = json.loads(result.text)
        assert "error" in data
        assert "already exists" in data["error"]


class TestPatternMethods:
    """Test individual pattern methods"""

    @pytest.mark.asyncio
    async def test_pattern_methods_integration(
        self, pattern_server, mock_patterns_dir, monkeypatch
    ):
        """Test integration of pattern methods"""
        monkeypatch.setattr(Path, "home", lambda: mock_patterns_dir)
        pattern_server.fabric_patterns_dir = (
            mock_patterns_dir / ".config" / "fabric" / "patterns"
        )
        pattern_server.custom_patterns_dir = (
            mock_patterns_dir / ".config" / "custom_patterns"
        )

        # Test that the pattern server was initialized properly
        assert hasattr(pattern_server, "server")
        assert hasattr(pattern_server, "patterns_cache")
        assert hasattr(pattern_server, "fabric_patterns_dir")
        assert hasattr(pattern_server, "custom_patterns_dir")

        # Test that we can load and access patterns
        await pattern_server.load_patterns()
        assert len(pattern_server.patterns_cache) == 2

        # Test search functionality
        result = await pattern_server.search_patterns("test")
        data = json.loads(result.text)
        assert len(data["results"]) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
