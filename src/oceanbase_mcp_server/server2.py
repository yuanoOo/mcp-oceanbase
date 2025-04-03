import logging
import os
from dotenv import load_dotenv
from mysql.connector import connect, Error
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("oceanbase_mcp_server")

load_dotenv()


def get_db_config():
    """Get database configuration from environment variables."""
    config = {
        "host": os.getenv("OB_HOST", "localhost"),
        "port": int(os.getenv("OB_PORT", "2881")),
        "user": os.getenv("OB_USER"),
        "password": os.getenv("OB_PASSWORD"),
        "database": os.getenv("OB_DATABASE")
    }

    if not all([config["user"], config["password"], config["database"]]):
        logger.error("Missing required database configuration. Please check environment variables:")
        logger.error("OB_USER, OB_PASSWORD, and OB_DATABASE are required")
        raise ValueError("Missing required database configuration")

    return config


# Initialize server
app = FastMCP("oceanbase_mcp_server")


@app.resource("oceanbase://sample/{table}", description="list all tables")
def list_resources(table: str) -> str:
    """List OceanBase tables as resources."""
    config = get_db_config()
    try:
        with connect(**config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {table} LIMIT 100")
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                result = [",".join(map(str, row)) for row in rows]
                return "\n".join([",".join(columns)] + result)

    except Error as e:
        return f"Failed to sample table: {table}"


@app.resource("oceanbase://tables", description="list all tables")
def list_resources() -> str:
    """List OceanBase tables as resources."""
    config = get_db_config()
    try:
        with connect(**config) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                logger.info(f"Found tables: {tables}")
                resp_header = "Columns info of this table: \n"
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                result = [",".join(map(str, row)) for row in rows]
                return resp_header + ("\n".join([",".join(columns)] + result))
    except Error as e:
        logger.error(f"Failed to list tables: {str(e)}")
        return "Failed to list tables"


@app.tool(name="execute_sql", description="Execute an SQL query on the OceanBase server")
def call_tool(query: str) -> str:
    """Execute SQL commands."""
    config = get_db_config()
    logger.info(f"Calling tool: execute_sql  with arguments: {query}")

    try:
        with connect(**config) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)

                # Special handling for SHOW TABLES
                if query.strip().upper().startswith("SHOW TABLES"):
                    tables = cursor.fetchall()
                    result = ["Tables_in_" + config["database"]]  # Header
                    result.extend([table[0] for table in tables])
                    return "\n".join(result)

                elif query.strip().upper().startswith("SHOW COLUMNS"):
                    resp_header = "Columns info of this table: \n"
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    result = [",".join(map(str, row)) for row in rows]
                    return resp_header + ("\n".join([",".join(columns)] + result))

                elif query.strip().upper().startswith("DESCRIBE"):
                    resp_header = "Description of this table: \n"
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    result = [",".join(map(str, row)) for row in rows]
                    return resp_header + ("\n".join([",".join(columns)] + result))

                # Regular SELECT queries
                elif query.strip().upper().startswith("SELECT"):
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    result = [",".join(map(str, row)) for row in rows]
                    return "\n".join([",".join(columns)] + result)

                # Non-SELECT queries
                else:
                    conn.commit()
                    return f"Query executed successfully. Rows affected: {cursor.rowcount}"

    except Error as e:
        logger.error(f"Error executing SQL '{query}': {e}")
        return f"Error executing query: {str(e)}"


def main():
    """Main entry point to run the MCP server."""
    logger.info("Starting OceanBase MCP server...")
    config = get_db_config()
    logger.info(f"Database config: {config['host']}/{config['database']} as {config['user']}")
    app.run()


if __name__ == "__main__":
    app.run()
