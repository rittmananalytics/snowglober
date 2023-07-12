import unittest
from pprint import pprint
from snowglober.snowflake_connector import SnowflakeConnector

class TestSnowflakeConnector(unittest.TestCase):
    
    def setUp(self):
        """Set up the SnowflakeConnector instance before each test."""
        self.connector = SnowflakeConnector()
    
    def test_get_all_databases(self):
        databases = self.connector.get_all_databases()
        print("!!!!!!!!!!!!! Starting test_get_all_databases !!!!!!!!!!!!! \n")
        for db in databases:
            pprint(db)
            print()  # Add an empty line for better separation between items

    def test_get_all_users(self):
        users = self.connector.get_all_users()
        print("!!!!!!!!!!!!! Starting test_get_all_users !!!!!!!!!!!!! \n")
        for user in users:
            pprint(user)
            print()

    def test_get_all_warehouses(self):
        warehouses = self.connector.get_all_warehouses()
        print("!!!!!!!!!!!!! Starting test_get_all_warehouses !!!!!!!!!!!!! \n")
        for warehouse in warehouses:
            pprint(warehouse)
            print()

    def test_get_all_roles(self):
        roles = self.connector.get_all_roles()
        print("!!!!!!!!!!!!! Starting test_get_all_roles !!!!!!!!!!!!! \n")
        for role in roles:
            pprint(role)
            print()

if __name__ == "__main__":
    unittest.main()
