# server.py
from fastmcp import FastMCP
import logging
import psycopg2

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
          description="""Retrieve a user's name from PostgreSQL using their IDReturn the name of the user with the given ID.

    The function is a thin wrapper around a parameterised SELECT that
    guarantees protection against SQL‑injection, automatically
    closes the connection/cursor and logs every step.
    """)
async def get_user_name_by_id(user_id: str) -> str:
    """
    Return the name of the user with the given ID.

    The function is a thin wrapper around a parameterised SELECT that
    guarantees protection against SQL‑injection, automatically
    closes the connection/cursor and logs every step.
    """
    logging.debug(f"Fetching user name for ID: {user_id}")

    # ---- 2️⃣  Configuración de conexión (puedes moverla a variables de entorno) ----
    db_config = {
        'dbname':   'mydatabase',
        'user':     'myuser',
        'password': 'mypassword',
        'host':     'localhost',
        'port':     5432
    }

    # ---- 3️⃣  Conexión y consulta con context managers ----
    try:
        # Construimos la cadena de conexión
        conn_str = (
            f"dbname={db_config['dbname']} "
            f"user={db_config['user']} "
            f"password={db_config['password']} "
            f"host={db_config['host']} "
            f"port={db_config['port']}"
        )

        async with psycopg2.connect(conn_str) as conn:
            async with conn.cursor() as cur:
                # Parámetro seguro, evita inyección SQL
                query = sql.SQL(f"SELECT name FROM users WHERE id = {user_id};")
                await cur.execute(query)

                # Recuperamos el resultado
                result = cur.fetchone()

        # ---- 4️⃣  Procesamos el resultado ----
        logging.info(f"Result: {result}")
        if result:
            logging.info(f"Returning: {result[0]}")

            return f"User name: {result[0]}" 
        else:
            return "User not found"

    except psycopg2.Error as e:            # Captura errores específicos de PostgreSQL
        logging.error(f"Database error: {e}")
        return "Error retrieving user"
    except Exception as e:                  # Captura cualquier otro error
        logging.error(f"Unexpected error: {e}")
        return "Error retrieving user"

