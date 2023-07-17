import os
from dotenv import load_dotenv
from snowflake.connector import connect, DictCursor


class SnowflakeConnector:

    def __init__(self):
        load_dotenv()
        self.user = os.getenv('SNOWFLAKE_USERNAME')
        self.password = os.getenv('SNOWFLAKE_PASSWORD')
        self.account = os.getenv('SNOWFLAKE_ACCOUNT')
        self.warehouse = os.getenv('SNOWFLAKE_WAREHOUSE')
        self.database = os.getenv('SNOWFLAKE_DATABASE')
        self.schema = os.getenv('SNOWFLAKE_SCHEMA')
        self.role = os.getenv('SNOWFLAKE_ROLE')
        self.connection = self._connect()

    def _connect(self):
        """Establishes a connection to Snowflake."""
        return connect(
            user=self.user,
            password=self.password,
            account=self.account,
            warehouse=self.warehouse,
            database=self.database,
            schema=self.schema,
            role=self.role
        )

    def _execute_query(self, query):
        cur = self.connection.cursor(DictCursor)
        try:
            cur.execute(query)
            return cur.fetchall()
        finally:
            cur.close()

    def get_all_databases(self):
        query = "show databases"
        return self._execute_query(query)
    
    def get_all_roles(self):
        query = "show roles"
        return self._execute_query(query)

    def get_all_users(self):
        query = "show users"
        return self._execute_query(query)

    def get_all_warehouses(self):
        query = "show warehouses"
        return self._execute_query(query)
