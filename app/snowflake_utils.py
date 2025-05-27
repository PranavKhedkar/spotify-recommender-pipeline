import os
from dotenv import load_dotenv
import snowflake.connector
from time import sleep

# Access the environment variables
account = os.getenv("SNOWFLAKE_ACCOUNT")
user = os.getenv("SNOWFLAKE_USER")
password = os.getenv("SNOWFLAKE_PASSWORD")
role = os.getenv("SNOWFLAKE_ROLE")
warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")
database = os.getenv("SNOWFLAKE_DATABASE")
schema = os.getenv("SNOWFLAKE_SCHEMA")


def connect_to_snowflake():
    """
    Connect to snowflake.

    Args:
        None

    Returns:
        conn: Snowflake connection object
    """
    try:
        conn = snowflake.connector.connect(
            account = account,
            user = user,
            password = password,
            role = role,
            warehouse = warehouse,
            database = database,
            schema = schema
        )

        return conn
    except Exception as e:
        print("Error reconnecting:", e)
        sleep(5)  # Wait for 5 seconds before trying again
        return connect_to_snowflake()
