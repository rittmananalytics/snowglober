# bootstrapping file; the orchestrator of the application

from snowglober.snowflake_connector import SnowflakeConnector
from generate_tf_config import TerraformConfigGenerator

def main():
    connector = SnowflakeConnector()
    generator = TerraformConfigGenerator(connector)
    generator.write_config_to_file()

if __name__ == "__main__":
    main()


