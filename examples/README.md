# Example Patterns

This directory contains example patterns to demonstrate the capabilities of the Pattern MCP Server.

## Available Examples

### Blog Analysis (`blog_analysis.md`)
Analyzes blog posts for content quality, structure, engagement, and SEO optimization. Perfect for content creators who want to improve their writing and reach.

**Use cases:**
- Review draft posts before publishing
- Audit existing content for improvements
- Analyze competitor content
- Get feedback on messaging and structure

### Code Security Review (`code_security_review.md`) 
Comprehensive security review focusing on OWASP Top 10 vulnerabilities and secure coding practices. Essential for defensive security reviews.

**Use cases:**
- Pre-deployment security checks
- Educational security analysis
- Vulnerability assessment
- Code audit for security compliance

### Zettelkasten Note Analyzer (`zettelkasten_analyzer.md`)
Analyzes notes for Zettelkasten best practices including atomicity, connectivity, and metadata organization. Perfect for knowledge workers building personal knowledge management systems.

**Use cases:**
- Improve note-taking for research and learning
- Build better connected knowledge graphs  
- Optimize notes for long-term knowledge retention
- Develop atomic thinking and writing practices

## How to Use These Examples

1. **Copy to your custom patterns directory:**
   ```bash
   cp examples/*.md ~/.config/custom_patterns/
   cp examples/*.json ~/.config/custom_patterns/
   ```

2. **Test with the MCP server:**
   - Start the pattern server
   - Use "List all available patterns" to see them
   - Use "Get the content of the 'blog_analysis' pattern" to retrieve

3. **Customize for your needs:**
   - Modify the prompts to match your specific requirements
   - Add your own metadata and tags
   - Create variations for different use cases

## Creating Your Own Patterns

Each pattern consists of:
- **`.md` file**: The actual prompt content
- **`.json` file**: Metadata with description, tags, use cases

### Pattern Best Practices

1. **Be Specific**: Clear, detailed instructions work better than vague requests
2. **Structure Output**: Use headers and bullet points for organized responses
3. **Include Context**: Explain the role/expertise level expected
4. **Add Examples**: Show what good output looks like
5. **Version Control**: Track changes and improvements over time

## Blog Post Ideas

These examples demonstrate:
- **Personal Knowledge Management**: Building your own prompt library
- **Quality Control**: Standardizing analysis and review processes  
- **Workflow Integration**: Seamless integration with your development tools
- **Knowledge Sharing**: Team patterns and organizational prompts