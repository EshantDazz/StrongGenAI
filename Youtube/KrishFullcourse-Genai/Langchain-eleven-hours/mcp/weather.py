from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Weather")  # Weather is the tool name


@mcp.tool()
def get_weather(city: str) -> str:
    """_summary_
    Get the current weather for a given city.
    """
    # In a real implementation, you would call a weather API here.
    # For demonstration purposes, we'll return a dummy weather report.
    return f"The current weather in {city} is sunny with a temperature of 25°C."


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
# streamable-http allows for real-time streaming of responses, which can be useful for long-running tasks or when you want to provide updates as they happen.
