import json
import os
import textwrap

class TerraformConfigGenerator:
    def __init__(self, connector):
        self.connector = connector

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
        resources = []

        for database in databases:
            resource = {
                "type": "snowflake_database",
                "name": database['name'],
                "properties": {
                    "name": database['name'],
                    "comment": database['comment'],
                    "data_retention_time_in_days": database['retention_time']
                }
            }
            resources.append(resource)
        return resources

    def _generate_resource_config_for_all_roles(self):
        print("Querying Snowflake for all roles...")
        roles = self.connector.get_all_roles()
        resources = []

        for role in roles:
            resource = {
                "type": "snowflake_role",
                "name": role['name'],
                "properties": {
                    "name": role['name'],
                    "comment": role['comment']
                }
            }
            resources.append(resource)
        return resources

    def _generate_resource_config_for_all_users(self):
        print("Querying Snowflake for all users...")
        users = self.connector.get_all_users()
        resources = []

        for user in users:
            resource = {
                "type": "snowflake_user",
                "name": user['name'],
                "properties": {
                    "name": user['name'],
                    "login_name": user['login_name'],
                    "comment": user['comment'],
                    "disabled": user['disabled'].lower(),
                    "display_name": user['display_name'],
                    "email": user['email'],
                    "first_name": user['first_name'],
                    "last_name": user['last_name'],
                    "default_warehouse": user['default_warehouse'],
                    "default_role": user['default_role'],
                    "must_change_password": user['must_change_password'].lower(),
                }
            }
            # If optional fields 'default_namespace' and 'default_secondary_roles' are present, add them to properties
            if user['default_namespace']:
                resource["properties"]["default_namespace"] = user['default_namespace']
            if user['default_secondary_roles']:
                resource["properties"]["default_secondary_roles"] = user['default_secondary_roles']

            resources.append(resource)
        return resources


    def _generate_resource_config_for_all_warehouses(self):
        print("Querying Snowflake for all warehouses...")
        warehouses = self.connector.get_all_warehouses()
        resources = []

        for warehouse in warehouses:
            resource = {
                "type": "snowflake_warehouse",
                "name": warehouse['name'],
                "properties": {
                    "name": warehouse['name'],
                    "comment": warehouse['comment'],
                    "warehouse_size": warehouse['size'],
                    "auto_suspend": int(warehouse['auto_suspend']),
                    "auto_resume": str(warehouse['auto_resume'].lower() == 'true').lower(),
                "initially_suspended": str(warehouse['state'].upper() == 'SUSPENDED').lower(),
                "scaling_policy": warehouse['scaling_policy'],
                "min_cluster_count": int(warehouse['min_cluster_count']),
                "max_cluster_count": int(warehouse['max_cluster_count'])
                }
            }
            resources.append(resource)
        return resources

    def write_resource_configs_to_tf_files(self):
        # Create target directory if it doesn't exist
        os.makedirs('target', exist_ok=True)

        # List of resource types and corresponding config generation methods
        resources_to_generate = [
            {"resource_type": "databases", "generation_method": self._generate_resource_config_for_all_databases},
            {"resource_type": "roles", "generation_method": self._generate_resource_config_for_all_roles},
            {"resource_type": "users", "generation_method": self._generate_resource_config_for_all_users},
            {"resource_type": "warehouses", "generation_method": self._generate_resource_config_for_all_warehouses},
        ]

        # Generate config for each resource type and write to file
        for resource_info in resources_to_generate:
            config = resource_info["generation_method"]()
            print(f'Generating config for {resource_info["resource_type"]} at target/{resource_info["resource_type"]}.tf...')
            with open(f'target/{resource_info["resource_type"]}.tf', 'w') as f:
                for resource in config:
                    f.write("resource \"{}\" \"{}\" {{\n".format(resource["type"], resource["name"]))
                    for property, value in resource["properties"].items():
                        f.write("    {} = \"{}\"\n".format(property, value))
                    f.write("}\n\n")