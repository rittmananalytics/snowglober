import os
from dotenv import load_dotenv
from snowflake.connector import connect, DictCursor


class SnowflakeConnector:

    def __init__(self):
        """
        This method initializes the SnowflakeConnector class and
        loads the environment variables from the .env file.
        """
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
        """
        This method establishes a connection to Snowflake using the
        environment variables defined in the .env file.
        """
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
        """
        This method executes a query against Snowflake and returns
        the results.
        """
        cur = self.connection.cursor(DictCursor)
        try:
            cur.execute(query)
            return cur.fetchall()
        finally:
            cur.close()

    def get_all_objects_of_a_resource_type(self, entity):
        """
        This method returns a list of all instances of the specified entity in Snowflake.
        The entity should be one of: databases, roles, users, warehouses.
        """
        query = f"show {entity}"
        return self._execute_query(query)
