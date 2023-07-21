import unittest
from pprint import pprint
from snowglober.snowflake_connector import SnowflakeConnector

class TestSnowflakeConnector(unittest.TestCase):
    
    def setUp(self):
        """Set up the SnowflakeConnector instance before each test."""
        self.connector = SnowflakeConnector()
    
    def test_get_all_snowflake_objects_of_a_resource_types(self):
        entities = 'schemas'
        resource_objects = self.connector.get_all_objects_of_a_resource_type(entities)
        print(f"!!!!!!!!!!!!! Starting test_get_all_{entities} !!!!!!!!!!!!! \n")
        for resource_object in resource_objects:
            pprint(resource_object)
            print()  # Add an empty line for better separation between items

if __name__ == "__main__":
    unittest.main()
