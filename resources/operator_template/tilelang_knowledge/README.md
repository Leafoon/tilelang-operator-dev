# Local Knowledge Base (Optional)

This directory is for local knowledge base overrides.

## Usage

If you want to customize the knowledge base for your specific operators:

1. Copy the knowledge base from `tilelang-operator-dev/resources/tilelang_knowledge/`
2. Modify the files as needed
3. Place them in this directory

The MCP server will use the local `tilelang_knowledge/` if it exists,
is complete enough, and parses cleanly. Otherwise it falls back to the
built-in knowledge base.

## Structure

```
tilelang_knowledge/
├── retrieval_plan.md      # Retrieval strategy document
├── capability_map.json    # Capability definitions
├── patterns.jsonl         # Implementation patterns
├── usage_patterns.jsonl   # Usage patterns and workflows
├── apis.jsonl             # API signatures
├── source_chunks.jsonl    # Source code fragments
├── troubleshooting.jsonl  # Common issue patterns and fixes
├── semantic_graph.json    # Entity relationship graph
├── semantic_graph.mmd     # Mermaid diagram
├── manifest.json          # Knowledge base manifest
└── README.md              # Knowledge base notes
```

## When to Use

- Adding operator-specific patterns
- Customizing device tuning recommendations
- Adding internal API documentation
- Adding internal troubleshooting records
- Overriding default retrieval behavior
