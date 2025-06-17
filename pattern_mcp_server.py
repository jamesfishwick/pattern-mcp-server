#!/usr/bin/env python3
"""
Pattern Content MCP Server

Exposes pattern/prompt content from Fabric and custom directories
for direct use by LLMs via the Model Context Protocol.
"""

import os
import asyncio
import json
from pathlib import Path
from typing import Dict, List, Optional
import mcp
from mcp.server import Server
from mcp.types import (
    Tool,
    TextContent,
    Resource,
    ResourceTemplate,
    ResourceContents
)

class PatternServer:
    def __init__(self):
        self.server = Server("pattern-content-server")
        self.fabric_patterns_dir = Path.home() / ".config" / "fabric" / "patterns"
        self.custom_patterns_dir = Path.home() / ".config" / "custom_patterns"

        # Ensure custom directory exists
        self.custom_patterns_dir.mkdir(parents=True, exist_ok=True)

        # Cache for patterns
        self.patterns_cache: Dict[str, Dict[str, str]] = {}

        # Setup handlers
        self.setup_handlers()

    def setup_handlers(self):
        """Setup MCP protocol handlers"""

        @self.server.list_tools()
        async def list_tools():
            """List available tools"""
            return [
                Tool(
                    name="list_patterns",
                    description="List all available patterns from Fabric and custom directories",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "source": {
                                "type": "string",
                                "enum": ["all", "fabric", "custom"],
                                "description": "Filter patterns by source",
                                "default": "all"
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Filter patterns by tags (if metadata available)"
                            }
                        }
                    }
                ),
                Tool(
                    name="get_pattern",
                    description="Get the content of a specific pattern",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Name of the pattern to retrieve"
                            }
                        },
                        "required": ["name"]
                    }
                ),
                Tool(
                    name="search_patterns",
                    description="Search patterns by content or description",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query to find in pattern content or metadata"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results to return",
                                "default": 10
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="create_pattern",
                    description="Create a new custom pattern",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Name for the new pattern"
                            },
                            "content": {
                                "type": "string",
                                "description": "The pattern content/prompt"
                            },
                            "metadata": {
                                "type": "object",
                                "description": "Optional metadata (tags, description, etc.)"
                            }
                        },
                        "required": ["name", "content"]
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict):
            """Handle tool calls"""

            if name == "list_patterns":
                result = await self.list_patterns(
                    source=arguments.get("source", "all"),
                    tags=arguments.get("tags", [])
                )
                return [result]

            elif name == "get_pattern":
                result = await self.get_pattern(arguments["name"])
                return [result]

            elif name == "search_patterns":
                result = await self.search_patterns(
                    arguments["query"],
                    arguments.get("limit", 10)
                )
                return [result]

            elif name == "create_pattern":
                result = await self.create_pattern(
                    arguments["name"],
                    arguments["content"],
                    arguments.get("metadata", {})
                )
                return [result]

            else:
                raise ValueError(f"Unknown tool: {name}")

        @self.server.list_resources()
        async def list_resources():
            """List patterns as browsable resources"""
            resources = []

            # Load all patterns
            await self.load_patterns()

            for pattern_name in self.patterns_cache:
                resources.append(
                    Resource(
                        uri=mcp.types.AnyUrl(f"pattern://{pattern_name}"),
                        name=pattern_name,
                        mimeType="text/markdown",
                        description=f"Pattern: {pattern_name}"
                    )
                )

            return resources

        @self.server.read_resource()
        async def read_resource(uri: mcp.types.AnyUrl):
            """Read a pattern resource"""
            uri_str = str(uri)
            if uri_str.startswith("pattern://"):
                pattern_name = uri_str.replace("pattern://", "")
                result = await self.get_pattern(pattern_name)

                return [mcp.types.ReadResourceContents(
                    type="text",
                    text=result.content[0].text
                )]

            raise ValueError(f"Unknown resource URI: {uri}")

    async def load_patterns(self):
        """Load all patterns into cache"""
        self.patterns_cache.clear()

        # Load Fabric patterns
        if self.fabric_patterns_dir.exists():
            for pattern_dir in self.fabric_patterns_dir.iterdir():
                if pattern_dir.is_dir():
                    system_file = pattern_dir / "system.md"
                    user_file = pattern_dir / "user.md"

                    if system_file.exists() or user_file.exists():
                        pattern_data = {
                            "name": pattern_dir.name,
                            "source": "fabric",
                            "path": str(pattern_dir)
                        }

                        if system_file.exists():
                            pattern_data["system"] = system_file.read_text()

                        if user_file.exists():
                            pattern_data["user"] = user_file.read_text()

                        self.patterns_cache[pattern_dir.name] = pattern_data

        # Load custom patterns
        if self.custom_patterns_dir.exists():
            for pattern_file in self.custom_patterns_dir.glob("*.md"):
                pattern_name = pattern_file.stem

                # Check for metadata file
                metadata_file = self.custom_patterns_dir / f"{pattern_name}.json"
                metadata = {}
                if metadata_file.exists():
                    metadata = json.loads(metadata_file.read_text())

                self.patterns_cache[pattern_name] = {
                    "name": pattern_name,
                    "source": "custom",
                    "path": str(pattern_file),
                    "content": pattern_file.read_text(),
                    "metadata": metadata
                }

    async def list_patterns(self, source: str = "all", tags: List[str] = None):
        """List available patterns"""
        await self.load_patterns()

        patterns = []
        for name, data in self.patterns_cache.items():
            # Filter by source
            if source != "all" and data["source"] != source:
                continue

            # Filter by tags if provided
            if tags and data.get("metadata", {}).get("tags"):
                pattern_tags = data["metadata"]["tags"]
                if not any(tag in pattern_tags for tag in tags):
                    continue

            patterns.append({
                "name": name,
                "source": data["source"],
                "description": data.get("metadata", {}).get("description", ""),
                "tags": data.get("metadata", {}).get("tags", [])
            })

        return TextContent(
            type="text",
            text=json.dumps({
                "patterns": patterns,
                "total": len(patterns)
            }, indent=2)
        )

    async def get_pattern(self, name: str):
        """Get pattern content"""
        await self.load_patterns()

        if name not in self.patterns_cache:
            return TextContent(
                type="text",
                text=json.dumps({
                    "error": f"Pattern '{name}' not found"
                })
            )

        pattern = self.patterns_cache[name]

        # Format content based on pattern type
        if pattern["source"] == "fabric":
            content = ""
            if "system" in pattern:
                content += f"# System Prompt\n\n{pattern['system']}\n\n"
            if "user" in pattern:
                content += f"# User Prompt\n\n{pattern['user']}"
        else:
            content = pattern["content"]

        return TextContent(
            type="text",
            text=json.dumps({
                "name": name,
                "source": pattern["source"],
                "content": content,
                "metadata": pattern.get("metadata", {})
            }, indent=2)
        )

    async def search_patterns(self, query: str, limit: int = 10):
        """Search patterns by content"""
        await self.load_patterns()

        results = []
        query_lower = query.lower()

        for name, data in self.patterns_cache.items():
            score = 0

            # Check name
            if query_lower in name.lower():
                score += 10

            # Check content
            content = ""
            if data["source"] == "fabric":
                content = data.get("system", "") + data.get("user", "")
            else:
                content = data.get("content", "")

            if query_lower in content.lower():
                score += 5

            # Check metadata
            if data.get("metadata"):
                desc = data["metadata"].get("description", "").lower()
                if query_lower in desc:
                    score += 3

                tags = data["metadata"].get("tags", [])
                if any(query_lower in tag.lower() for tag in tags):
                    score += 2

            if score > 0:
                results.append({
                    "name": name,
                    "source": data["source"],
                    "score": score,
                    "description": data.get("metadata", {}).get("description", "")
                })

        # Sort by score and limit
        results.sort(key=lambda x: x["score"], reverse=True)
        results = results[:limit]

        return TextContent(
            type="text",
            text=json.dumps({
                "results": results,
                "total": len(results)
            }, indent=2)
        )

    async def create_pattern(self, name: str, content: str, metadata: Dict):
        """Create a new custom pattern"""
        pattern_file = self.custom_patterns_dir / f"{name}.md"

        if pattern_file.exists():
            return TextContent(
                type="text",
                text=json.dumps({
                    "error": f"Pattern '{name}' already exists"
                })
            )

        # Save pattern content
        pattern_file.write_text(content)

        # Save metadata if provided
        if metadata:
            metadata_file = self.custom_patterns_dir / f"{name}.json"
            metadata_file.write_text(json.dumps(metadata, indent=2))

        # Reload cache
        await self.load_patterns()

        return TextContent(
            type="text",
            text=json.dumps({
                "message": f"Pattern '{name}' created successfully",
                "path": str(pattern_file)
            })
        )

    async def run(self):
        """Run the MCP server"""
        async with mcp.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    server = PatternServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())