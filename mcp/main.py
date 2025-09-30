# server.py
from fastmcp import FastMCP
import logging
import psycopg2
import asyncio

logging.basicConfig(level=logging.DEBUG)
# Create an MCP server
mcp = FastMCP(name="wheather")

# Add an addition tool

# Rename the second add function to greet and update tool metadata
# @mcp.tool(name="Dynamic greeting", description="Generate a greeting specific to name passed as parameter")
# def greet(name: str) -> str:
#     """Return a personalized greeting."""
#     logging.debug("Dynamic greeting tool called.")
#     return f"hola {name} hace frio"

# New tool: fetch user name by ID
import logging
import psycopg2
from psycopg2 import sql

# ------------------------------------------------------------------
# 1️⃣  Decorador que proviene de tu framework (mcp)
# ------------------------------------------------------------------
@mcp.tool(name="Get user name by ID",
          description="""Retrieve a user's name from PostgreSQL using their ID. Return the name of the user with the given ID.

    The function is a thin wrapper around a parameterised SELECT that
    guarantees protection against SQL‑injection, automatically
    closes the connection/cursor and logs every step.
    """)
def get_user_name_by_id(user_id: str) -> str:
    logging.debug(f"Fetching user name for ID: {user_id}")

    db_config = {
        'dbname':   'mydatabase',
        'user':     'myuser',
        'password': 'mypassword',
        'host':     'localhost',
        'port':     5433
    }

    conn_str = (
        f"dbname={db_config['dbname']} "
        f"user={db_config['user']} "
        f"password={db_config['password']} "
        f"host={db_config['host']} "
        f"port={db_config['port']}"
    )

    try:
        with psycopg2.connect(conn_str) as conn:
            with conn.cursor() as cur:
                query = sql.SQL("SELECT name FROM users WHERE id = %s;")
                cur.execute(query, (user_id,))
                result = cur.fetchone()

        logging.info(f"Result: {result}")
        if result:
            logging.info(f"Returning: {result[0]}")
            return f"User name: {result[0]}"
        else:
            return "User not found"

    except psycopg2.Error as e:
        logging.error(f"Database error: {e}")
        return "Error retrieving user"
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return "Error retrieving user"
            

    except psycopg2.Error as e:            # Captura errores específicos de PostgreSQL
        logging.error(f"Database error: {e}")
        return "Error retrieving user"
    except Exception as e:                  # Captura cualquier otro error
        logging.error(f"Unexpected error: {e}")
        return "Error retrieving user"

