# bootstrapping file; the orchestrator of the application

from snowglober.snowflake_connector import SnowflakeConnector
from generate_tf_config import TerraformConfigGenerator

def main():
    connector = SnowflakeConnector()
    generator = TerraformConfigGenerator(connector)
    generator.generate_variables_tf_file()
    generator.generate_providers_tf_file()
    generator.add_missing_environment_variables_to_tfvars_file()
    generator.write_resource_configs_to_tf_files()
    generator.run_terraform_init()
    generator.import_resources()
    generator.update_tf_files_with_optional_properties()

if __name__ == "__main__":
    main()
    print("Snowglober has successfully finished generating Terraform configs!")


