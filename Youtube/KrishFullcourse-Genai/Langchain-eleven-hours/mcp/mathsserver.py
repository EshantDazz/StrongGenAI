from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Math")  # Math is the tool name


@mcp.tool()
def add(a: int, b: int) -> int:
    """_suummary_
    add two numbers
    """
    return a + b


@mcp.tool()
def multiply(a: int, b: int) -> int:
    """_summary_
    multiply two numbers
    """
    return a * b


if __name__ == "__main__":
    mcp.run(transport="stdio")

# stdio is useful for testing locally, but for production,
# you may want to use a different transport like "http"
# or "websocket" depending on your deployment needs.
