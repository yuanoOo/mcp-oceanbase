from oceanbase_mcp_server import server
from . import server_on_fastmcp
import asyncio
import argparse

from . import server


def main():
    """Main entry point for the package."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--legacy", type=bool, default=False, help="Whether to enable legacy mode."
    )
    parser.add_argument(
        "--transport", type=str, default="stdio", help="Whether to enable legacy mode."
    )
    args = parser.parse_args()

    if args.legacy:
        asyncio.run(server.main())
    else:
        if args.transport == "stdio":
            server_on_fastmcp.main()
        else:
            server_on_fastmcp.main(transport="sse")


# Expose important items at package level
__all__ = ["main", "server"]
