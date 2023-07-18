import json
import os
import re
import subprocess
import textwrap

class TerraformConfigGenerator:
    def __init__(self, connector):
        self.connector = connector
        self.resource_mapping = {}  # This will hold the mapping between Terraform resource names and cloud IDs

        # Create target directory if it doesn't exist
        os.makedirs('target', exist_ok=True)

        # Define resources_to_generate as an instance attribute
        self.resources_to_generate = [
            {"resource_type": "snowflake_database", "generation_method": self._generate_resource_config_for_all_databases},
            {"resource_type": "snowflake_role", "generation_method": self._generate_resource_config_for_all_roles},
            {"resource_type": "snowflake_user", "generation_method": self._generate_resource_config_for_all_users},
            {"resource_type": "snowflake_warehouse", "generation_method": self._generate_resource_config_for_all_warehouses},
        ]

    def generate_variables_tf_file(self):

        print("Generating variables.tf...")
        variables = [
            "snowflake_account",
            "snowflake_role",
            "snowflake_warehouse",
            "snowflake_username",
            "snowflake_password",
        ]
        
        # Generate config string
        config_lines = []
        for variable in variables:
            config_lines.append(f"variable \"{variable}\" {{}}")
            
        config = "\n".join(config_lines)
        
        # Write to file
        with open('target/variables.tf', 'w') as f:
            f.write(config)

        print("Generating variables.tf...done")

    def generate_providers_tf_file(self):

        print("Generating providers.tf...")
        config = textwrap.dedent("""\
        terraform {
          required_providers {
            snowflake = {
              source = "Snowflake-Labs/snowflake"
            #   version = "3.5.1"
            }
          }
        }

        provider "snowflake" {
          account   = var.snowflake_account
          role      = var.snowflake_role
          warehouse = var.snowflake_warehouse
          username  = var.snowflake_username
          password  = var.snowflake_password
        }
        """)

        with open('target/providers.tf', 'w') as f:
            f.write(config)

        print("Generating providers.tf...done")

    def add_missing_environment_variables_to_tfvars_file(self):

        print("Generating terraform.tfvars...")
        variables = {
            "snowflake_account": "",
            "snowflake_role": "",
            "snowflake_warehouse": "",
            "snowflake_username": "",
            "snowflake_password": "",
        }
        
        # Update variables with values from environment variables
        for key in variables:
            env_value = os.environ.get(key.upper())
            if env_value:
                variables[key] = env_value
        
        existing_vars = {}
        
        # Read existing terraform.tfvars file
        if os.path.exists('target/terraform.tfvars'):
            with open('target/terraform.tfvars', 'r') as f:
                lines = f.readlines()
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith("#"):  # Ignore blank lines and comments
                        key, value = line.split("=", 1)
                        existing_vars[key.strip()] = value.strip()

        # Generate config string
        config_lines = []
        for key, value in variables.items():
            if key not in existing_vars:  # Only add variables that are not already in the file
                config_lines.append(f"{key} = \"{value}\"")
                print(f"Added this environment variable to terraform.tfvars (only name shown): " + key)


        if not config_lines:  # No new variables to add
            print("No new variables to add to terraform.tfvars.")
            return

        config = "\n".join(config_lines)

        # Append to file
        with open('target/terraform.tfvars', 'a') as f:
            f.write("\n" + config)

    def _generate_resource_config_for_all_databases(self):

        print("Querying Snowflake for all databases...")
        databases = self.connector.get_all_databases()
        print("Querying Snowflake for all databases...done")

        resources = []

        for database in databases:
            resource = {
                "type": "snowflake_database",
                "name": database['name'],
                "properties": {
                    "name": database['name'],
                }
            }

            resources.append(resource)

            # Add to resource mapping for terraform import
            tf_resource_name = f"{resource['type']}.{resource['name']}"
            self.resource_mapping[tf_resource_name] = database['name']  # Assuming the 'name' property of database is the cloud ID

        return resources

    def _generate_resource_config_for_all_roles(self):

        print("Querying Snowflake for all roles...")
        roles = self.connector.get_all_roles()
        print("Querying Snowflake for all roles...done")

        resources = []

        for role in roles:
            resource = {
                "type": "snowflake_role",
                "name": role['name'],
                "properties": {
                    "name": role['name'],
                }
            }

            resources.append(resource)
        
            # Add to resource mapping for terraform import
            tf_resource_name = f"{resource['type']}.{resource['name']}"
            self.resource_mapping[tf_resource_name] = role['name']  # Assuming the 'name' property of role is the cloud ID

        return resources

    def _generate_resource_config_for_all_users(self):

        print("Querying Snowflake for all users...")
        users = self.connector.get_all_users()
        print("Querying Snowflake for all users...done")

        resources = []

        for user in users:

            # Don't generate config for "SNOWFLAKE"; a user that's setup by Snowflake for accessing the system stats
            if user['name'].upper() == 'SNOWFLAKE':
                continue

            resource = {
                "type": "snowflake_user",
                "name": user['name'],
                "properties": {
                    "name": user['name'],
                    "login_name": user['login_name'],
                }
            }
            # If optional fields 'default_namespace' and 'default_secondary_roles' are present, add them to properties
            if user['default_namespace']:
                resource["properties"]["default_namespace"] = user['default_namespace']
            if user['default_secondary_roles']:
                resource["properties"]["default_secondary_roles"] = user['default_secondary_roles']

            resources.append(resource)

            # Add to resource mapping for terraform import
            tf_resource_name = f"{resource['type']}.{resource['name']}"
            self.resource_mapping[tf_resource_name] = user['name']  # Assuming the 'name' property of user is the cloud ID

        return resources


    def _generate_resource_config_for_all_warehouses(self):

        print("Querying Snowflake for all warehouses...")
        warehouses = self.connector.get_all_warehouses()
        print("Querying Snowflake for all warehouses...done")

        resources = []

        for warehouse in warehouses:
            resource = {
                "type": "snowflake_warehouse",
                "name": warehouse['name'],
                "properties": {
                    "name": warehouse['name'],
                }
            }

            resources.append(resource)
        
            # Add to resource mapping for terraform import
            tf_resource_name = f"{resource['type']}.{resource['name']}"
            self.resource_mapping[tf_resource_name] = warehouse['name']  # Assuming the 'name' property of warehouse is the cloud ID

        return resources

    def write_resource_configs_to_tf_files(self):

        # Generate config for each resource type and write to file
        for resource_info in self.resources_to_generate:
            config = resource_info["generation_method"]()
            resource_type = resource_info["resource_type"]

            print(f'Generating config for {resource_type} at target/{resource_type}.tf...')
            
            with open(f'target/{resource_type}.tf', 'w') as f:
                for resource in config:
                    f.write("resource \"{}\" \"{}\" {{\n".format(resource["type"], resource["name"]))
                    for property, value in resource["properties"].items():
                        f.write("    {} = \"{}\"\n".format(property, value))
                    f.write("}\n\n")
            
            print(f'Generating config for {resource_type} at target/{resource_type}.tf...done')

    def run_terraform_init(self):

        # Run terraform init
        print("Running terraform init...")
        subprocess.run(["terraform", "-chdir=target", "init"], check=True)
        print("Running terraform init...done")

    def import_resources(self):

        # Delete existing .tfstate file if it exists
        tfstate_file_path = 'target/terraform.tfstate'
        if os.path.exists(tfstate_file_path):
            os.remove(tfstate_file_path)
            print(f"Deleted existing {tfstate_file_path} file.")

        # Import resources into Terraform state
        print("Importing resources into Terraform state...")
        for resource_name, resource_id in self.resource_mapping.items():
            subprocess.run(["terraform", "-chdir=target", "import", resource_name, resource_id], check=True)
        print("Importing resources into Terraform state...done")

    def update_tf_files_with_optional_properties(self):

        # Define the valid properties for each resource type
        valid_properties = {
            "snowflake_user": [
                "name", "comment", "default_namespace", "default_role",
                "default_secondary_roles", "default_warehouse", "disabled",
                "display_name", "email", "first_name", "last_name", "login_name",
                "must_change_password", "password", "rsa_public_key", "rsa_public_key_2"
            ],
            "snowflake_database": [
                "name", "comment", "data_retention_time_in_days", "from_database", "from_replica", 
                "from_share", "is_transient", "replication_configuration"
            ],
            "snowflake_role": [
                "name", "comment"
            ],
            "snowflake_warehouse": [
                "name", "auto_resume", "auto_suspend", "comment", "initially_suspended", 
                "max_cluster_count", "max_concurrency_level", "min_cluster_count", "resource_monitor", 
                "scaling_policy", "statement_queued_timeout_in_seconds", "statement_timeout_in_seconds", 
                "wait_for_provisioning", "warehouse_size"
            ]
        }

        # Check if .tfstate file exists
        tfstate_file_path = 'target/terraform.tfstate'
        if not os.path.exists(tfstate_file_path):
            print("No .tfstate file found. Run 'import_resources' first.")
            return

        print("Updating .tf files with optional properties...")

        # Load .tfstate file
        with open(tfstate_file_path, 'r') as f:
            tfstate_content = json.load(f)

        # Loop through each resource type
        for resource_info in self.resources_to_generate:
            
            resource_type = resource_info["resource_type"]

            tf_file_path = f'target/{resource_type}.tf'

            if not os.path.exists(tf_file_path):
                print(f'No .tf file found for {resource_type}. Skipping.')
                continue

            with open(tf_file_path, 'r') as f:
                tf_file_content = f.readlines()

            for resource in tfstate_content['resources']:
                if resource_info["resource_type"] == resource['type']:
                    for instance in resource['instances']:
                        instance_attributes = instance['attributes']

                        # Use regular expressions to match the resource line in the .tf file.
                        resource_type = resource['type']
                        resource_line_num = next((i for i, line in enumerate(tf_file_content) if re.match(f'resource "{resource_type}" "{instance_attributes["name"]}" {{', line.strip())), None)
                        
                        if resource_line_num is None:
                            print(f"Could not find resource {resource['type']} {instance_attributes['name']} in {tf_file_path}. Skipping.")
                            continue

                        # Find the line number of the closing bracket for this resource
                        resource_end_line_num = next((i for i, line in enumerate(tf_file_content[resource_line_num+1:], start=resource_line_num+1) if '}' in line), len(tf_file_content))

                        for key, value in instance_attributes.items():
                            if key not in valid_properties.get(resource_type, []):  # Check if the property is valid
                                continue
                            if value is None or (isinstance(value, list) and len(value) == 0):  # Skip properties with 'null' or empty array as value
                                continue
                            if not any(key in line for line in tf_file_content[resource_line_num:resource_end_line_num]):
                                if isinstance(value, bool):
                                    tf_file_content.insert(resource_end_line_num, f'    {key} = {str(value).lower()}\n')  # no quotes around boolean values
                                elif isinstance(value, list):
                                    tf_file_content.insert(resource_end_line_num, f'    {key} = {value}\n')  # no quotes around array values
                                else:
                                    tf_file_content.insert(resource_end_line_num, f'    {key} = "{value}"\n')
                                resource_end_line_num += 1  # increment the end line num to keep up with the added lines

            with open(tf_file_path, 'w') as f:
                f.writelines(tf_file_content)

        print("Updating .tf files with optional properties...done")
