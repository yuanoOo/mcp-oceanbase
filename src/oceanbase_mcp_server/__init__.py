from oceanbase_mcp_server import server
from . import server2
import asyncio
import argparse


def main():
    """Main entry point for the package."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--legacy', type=bool, default=False, help="Whether to enable legacy mode.")
    args = parser.parse_args()

    if args.legacy:
        asyncio.run(server.main())
    else:
        server2.main()


# Expose important items at package level
__all__ = ['main', 'server']
