# Pattern MCP Server

A Model Context Protocol (MCP) server that exposes pattern/prompt content from [Fabric](https://github.com/danielmiessler/fabric) and custom directories for direct use by LLMs.

## Why This Server?

Existing Fabric MCP implementations (like ksylvan/fabric-mcp) execute patterns through Fabric's configured LLM and relay the results back. This defeats the purpose of empowering your current LLM with Fabric's specialized prompts.

What this server does differently:

- **Exposes pattern content directly** - Returns the actual prompt text instead of executing it
- **No middleman execution** - Your LLM uses the patterns directly, maintaining context and conversation flow
- **Composable** - Combine multiple patterns or use parts of them
- **Extensible** - Easy to add new pattern sources or categories

This approach lets you leverage Fabric's carefully crafted prompts like `extract_wisdom`, `analyze_claims`, etc., while keeping the execution within your current LLM session.

## Features

- **Pattern Management**: List, search, and retrieve patterns from both Fabric and custom directories
- **Fabric Integration**: Automatically discovers and serves patterns from your Fabric installation
- **Custom Patterns**: Build your own prompt library in `~/.config/custom_patterns/`
- **Search & Discovery**: Find patterns by content, tags, or metadata
- **Resource Browsing**: Access patterns as browsable resources via MCP

## Installation

### 1. Create a project directory

```bash
mkdir ~/pattern-mcp-server
cd ~/pattern-mcp-server
```

### 2. Save the server code

Save the Python code as `pattern_mcp_server.py`

### 3. Create requirements.txt

```txt
mcp>=0.1.0
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
# or with uv:
uv pip install -r requirements.txt
```

### 5. Make the script executable

```bash
chmod +x pattern_mcp_server.py
```

### Using Virtual Environments (Recommended)

Virtual environments provide isolation and prevent dependency conflicts. Here's why and how to use them with the Pattern MCP Server:

**Key Benefits:**

- **Isolation**: Keeps MCP dependencies separate from system Python
- **Version Control**: No conflicts with other projects
- **Clean Uninstall**: Just delete the folder
- **Team Sharing**: Others can recreate your exact environment

**Setup with virtual environment:**

```bash
# Create virtual environment
python -m venv venv

# Activate it (Unix/macOS)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Use the provided run script
./run_pattern_mcp.sh
```

**Why use the wrapper script?**
The `run_pattern_mcp.sh` script is required because MCP clients can't activate virtual environments directly. The script:

- Activates the virtual environment
- Launches the Python server
- Ensures dependencies are properly isolated

**Alternative: Using UV for virtual environments:**

```bash
# UV automatically creates .venv
uv venv

# Install dependencies
uv pip install -r requirements.txt

# Update the run script to use .venv instead of venv
```

### Alternative Setup Approaches

**If you prefer a different location:**

```bash
# Put it in a development folder
mkdir ~/Development/pattern-mcp-server

# Or in a tools folder
mkdir ~/.local/tools/pattern-mcp-server
```

**If you're on Windows:**

```powershell
# PowerShell commands
mkdir $HOME\pattern-mcp-server
cd $HOME\pattern-mcp-server

# For virtual environment on Windows
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt
```

## MCP Client Configuration

Add this to your MCP client configuration (e.g., for Claude Desktop, Cursor, etc.):

```json
{
  "pattern-content": {
    "command": "python",
    "args": ["~/pattern-mcp-server/pattern_mcp_server.py"]
  }
}
```

Or if you prefer using the shebang:

```json
{
  "pattern-content": {
    "command": "~/pattern-mcp-server/pattern_mcp_server.py",
    "args": []
  }
}
```

Or if using the virtual environment run script (recommended):

```json
{
  "pattern-content": {
    "command": "/bin/bash",
    "args": ["~/pattern-mcp-server/run_pattern_mcp.sh"]
  }
}
```

**Important Notes:**

- The wrapper script approach with `/bin/bash` ensures proper virtual environment activation before running the server
- **Tilde (~) expansion may not work** in MCP configurations. If you get "No such file or directory" errors, use absolute paths (e.g., `/Users/yourusername/pattern-mcp-server/`) instead of `~/pattern-mcp-server/`
- Run `echo $HOME` to find your home directory path

## Directory Structure

The server expects/creates these directories:

```
~/.config/
├── fabric/
│   └── patterns/        # Fabric patterns (if you have Fabric installed)
│       ├── analyze_claims/
│       │   ├── system.md
│       │   └── user.md
│       └── extract_wisdom/
│           └── system.md
└── custom_patterns/     # Your custom patterns
    ├── my_prompt.md
    ├── my_prompt.json   # Optional metadata
    └── code_review.md
```

## Usage

### Running the Server

```bash
python pattern_mcp_server.py
```

The server runs as an MCP stdio server, ready to be connected by MCP clients.

### Available Tools

#### `list_patterns`

List all available patterns from Fabric and custom directories.

**Parameters:**

- `source` (optional): Filter by source - "all", "fabric", or "custom" (default: "all")
- `tags` (optional): Filter patterns by tags array

#### `get_pattern`

Retrieve the content of a specific pattern.

**Parameters:**

- `name` (required): Name of the pattern to retrieve

#### `search_patterns`

Search patterns by content or description.

**Parameters:**

- `query` (required): Search query string
- `limit` (optional): Maximum number of results (default: 10)

#### `create_pattern`

Create a new custom pattern.

**Parameters:**

- `name` (required): Name for the new pattern
- `content` (required): The pattern content/prompt
- `metadata` (optional): Metadata object (tags, description, etc.)

### Pattern Resources

All patterns are also exposed as MCP resources with URIs like:

- `pattern://extract_wisdom`
- `pattern://my_custom_prompt`

## Usage Examples

### 1. List all patterns

Ask me: "List all available patterns"

### 2. Get a specific pattern

Ask me: "Get the content of the 'extract_wisdom' pattern"

### 3. Search patterns

Ask me: "Search for patterns related to 'code review'"

### 4. Create a custom pattern

Ask me: "Create a pattern called 'meeting_notes' with this content: [your prompt]"

## Custom Pattern Format

### Simple Pattern (just markdown)

`~/.config/custom_patterns/code_review.md`:

```markdown
You are an expert code reviewer. Analyze the provided code for:

1. Code quality and readability
2. Potential bugs or issues
3. Performance concerns
4. Security vulnerabilities
5. Best practices adherence

Provide specific, actionable feedback with examples.
```

### Pattern with Metadata

`~/.config/custom_patterns/meeting_notes.json`:

```json
{
  "description": "Extract key points from meeting transcripts",
  "tags": ["meetings", "summary", "extraction"],
  "author": "Your Name",
  "version": "1.0"
}
```

## Example Patterns

See the [examples/](examples/) directory for complete example patterns including:

- **Blog Analysis** - Analyzes blog posts for content quality, structure, and SEO
- **Code Security Review** - Comprehensive security review focusing on OWASP Top 10
- **Zettelkasten Note Analyzer** - Analyzes notes for knowledge management best practices

Each example includes both the pattern content (`.md`) and metadata (`.json`) files to demonstrate best practices for pattern creation.

## Extending the Server

### Adding Pattern Categories

Modify the `__init__` method to add more pattern directories:

```python
self.team_patterns_dir = Path.home() / ".config" / "team_patterns"
self.project_patterns_dir = Path.home() / "projects" / "prompts"
```

### Adding Pattern Validation

Add validation in the `create_pattern` method:

```python
def validate_pattern(self, content: str) -> bool:
    # Check for required sections, length, etc.
    return True
```

### Adding Pattern Templates

Create template patterns that users can customize:

```python
TEMPLATES = {
    "code_analysis": "You are an expert...",
    "data_extraction": "Extract the following..."
}
```

## Tips

1. **Organize with Tags**: Use metadata files to tag and categorize your patterns
2. **Version Control**: Consider putting your custom_patterns directory in git
3. **Team Sharing**: Mount a shared directory for team patterns
4. **Pattern Composition**: Create patterns that reference other patterns

## Troubleshooting

1. **Server won't start**: Check Python version (3.8+) and MCP installation
2. **Patterns not found**: Ensure directories exist and have correct permissions
3. **Can't create patterns**: Check write permissions on custom_patterns directory
4. **"No such file or directory" error with run script**: The tilde (~) isn't being expanded in MCP configurations. Use absolute paths instead:

   ```bash
   # Find your home directory
   echo $HOME
   ```

   Then update your MCP configuration:

   ```json
   {
     "pattern-content": {
       "command": "/bin/bash",
       "args": ["/Users/yourusername/pattern-mcp-server/run_pattern_mcp.sh"]
     }
   }
   ```

   Alternative: Use the Python binary from the virtual environment directly:

   ```json
   {
     "pattern-content": {
       "command": "/Users/yourusername/pattern-mcp-server/venv/bin/python",
       "args": ["/Users/yourusername/pattern-mcp-server/pattern_mcp_server.py"]
     }
   }
   ```

## Requirements

- Python 3.8+
- mcp>=0.1.0

## Next Steps

1. Install Fabric to get access to its pattern library
2. Create your first custom patterns
3. Build pattern collections for specific domains
4. Share patterns with your team

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Author

Created by [James Fishwick](https://github.com/jamesfishwick) to provide direct access to prompt patterns for personal knowledge management and AI workflow optimization.

## Development

### Quick Start for Developers

```bash
# If you haven't activated your virtual environment yet:
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dev dependencies if not already installed:
pip install -r requirements-dev.txt

# Now you can run linting:
make lint
```

### Setting Up Development Environment

```bash
# Clone the repository
git clone <repository-url>
cd pattern-mcp-server

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Or use make commands after activating venv
make install-dev

# Set up pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run tests
make test

# Run tests with coverage
make test-cov

# View coverage report
open htmlcov/index.html
```

### Code Quality

```bash
# Run linting
make lint

# Format code
make format

# Run all pre-commit hooks
pre-commit run --all-files
```

### Available Make Commands

- `make install` - Install production dependencies
- `make install-dev` - Install development dependencies
- `make lint` - Run linting (ruff and mypy)
- `make format` - Format code with black and ruff
- `make test` - Run unit tests
- `make test-cov` - Run tests with coverage report
- `make clean` - Clean up generated files
- `make run` - Run the MCP server
- `make setup` - Full development environment setup

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting (`make test && make lint`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Code Style

- We use Black for code formatting
- Ruff for linting
- MyPy for type checking
- All code must pass the pre-commit hooks
- Maintain test coverage above 80%
