import json
import os
import re
import subprocess
import textwrap

class TerraformConfigGenerator:

    def __init__(self, connector):
        """
        This method is called when the class is instantiated.
        It sets up the class attributes.
        """
        self.connector = connector
        self.resource_mapping = {}  # This will hold the mapping between Terraform resource names and cloud IDs

        # Define common file paths
        self.tfstate_file_path = 'target/terraform.tfstate'
        self.tfvars_file_path = 'target/terraform.tfvars'
        self.tf_variables_file_path = 'target/variables.tf'
        self.tf_providers_file_path = 'target/providers.tf'

        # Create target directory if it doesn't exist
        os.makedirs('target', exist_ok=True)

        # Define resources_to_generate as an instance attribute
        self.resources_to_generate = [
            {"resource_type": "snowflake_database", "api_call": self.connector.get_all_databases},
            {"resource_type": "snowflake_role", "api_call": self.connector.get_all_roles},
            {"resource_type": "snowflake_user", "api_call": self.connector.get_all_users},
            {"resource_type": "snowflake_warehouse", "api_call": self.connector.get_all_warehouses}
        ]


        # Define valid_properties for each resource type TODO RENAME DICT?
        self.valid_properties = {
            "snowflake_database": {
                "required_properties": ["name"],
                "optional_properties": ["comment", "data_retention_time_in_days", "from_database", 
                                        "from_replica", "from_share", "is_transient", "replication_configuration",
                                        "from_database", "is_transient",],
                "names_to_ignore": [],
            },
            "snowflake_role": {
                "required_properties": ["name",],
                "optional_properties": ["comment",],
                "names_to_ignore": [],
            },
            "snowflake_user": {
                "required_properties": ["name", "login_name"],
                "optional_properties": ["comment", "default_namespace", "default_role", "default_secondary_roles", 
                                        "default_warehouse", "disabled", "display_name", "email", 
                                        "first_name", "last_name", "must_change_password", 
                                        "password", "rsa_public_key", "rsa_public_key_2", "tag",],
                "names_to_ignore": ["SNOWFLAKE"],
            },
            "snowflake_warehouse": {
                "required_properties": ["name",],
                "optional_properties": ["auto_resume", "auto_suspend", "comment", "initially_suspended", 
                                        "max_cluster_count", "max_concurrency_level", "min_cluster_count", 
                                        "resource_monitor", "scaling_policy", "statement_queued_timeout_in_seconds", 
                                        "statement_timeout_in_seconds", "wait_for_provisioning", "warehouse_size",
                                        "enable_query_acceleration", "query_acceleration_max_scale_factor",
                                        "warehouse_type",],
                "names_to_ignore": [],
            }
        }

    def generate_variables_tf_file(self):
        """
        This method generates the variables.tf file.
        It hardcodes the variables that are required for the Snowflake provider.
        """
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
        with open(self.tf_variables_file_path, 'w') as f:
            f.write(config)

        print("Generating variables.tf...done")

    def generate_providers_tf_file(self):
        """
        This method generates the providers.tf file.
        It hardcodes the Snowflake provider.
        """
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

        with open(self.tf_providers_file_path, 'w') as f:
            f.write(config)

        print("Generating providers.tf...done")

    def add_missing_environment_variables_to_tfvars_file(self):
        """
        This method adds any missing environment variables to the terraform.tfvars file.
        It takes them from the environment variables.
        If there is no terraform.tfvars file, it creates one.
        If there is a terraform.tfvars file, it adds any missing variables to the end of the file.
        If a variable already exists in the file, it is not overwritten.
        """
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
        if os.path.exists(self.tfvars_file_path):
            with open(self.tfvars_file_path, 'r') as f:
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
        with open(self.tfvars_file_path, 'a') as f:
            f.write("\n" + config)

    def _generate_resource_config_for_all_objects_of_a_resource_type(self, resource_type, get_all_func):
        """
        This method generates the config for all objects of a given resource type.
        It uses the get_all_func to get all objects of the given resource type.
        It then loops through each object and generates the config for it.
        It adds the config to the self.resources list.
        It also adds the resource to the self.resource_mapping dictionary for terraform import.
        It only generates config for objects that are not in the names_to_ignore list.
        Only required properties for each resource type are added to the config.
        """
        print(f"Querying Snowflake for all {resource_type}s...")
        all_resources = get_all_func()
        print(f"Querying Snowflake for all {resource_type}s...done")

        resources = []

        for resource in all_resources:

            # Don't generate config for any resource in names_to_ignore
            if resource['name'].upper() in map(str.upper, self.valid_properties[resource_type]["names_to_ignore"]):
                continue

            config_resource = {
                "type": resource_type,
                "name": resource['name'],
                "properties": {key: resource[key] for key in self.valid_properties[resource_type]["required_properties"] if key in resource}
            }

            resources.append(config_resource)

            # Add to resource mapping for terraform import
            tf_resource_name = f"{config_resource['type']}.{config_resource['name']}"
            self.resource_mapping[tf_resource_name] = resource['name']  # Assuming the 'name' property of resource is the cloud ID

        return resources

    def write_resource_configs_to_tf_files(self):
        """
        This method takes the self.resources list and writes the config to the target directory.
        It writes one file per resource type.
        It writes the config in the format that terraform expects.
        """
        # Generate config for each resource type and write to file
        for resource_info in self.resources_to_generate:
            resource_type = resource_info["resource_type"]
            api_call = resource_info["api_call"]

            # Call the new method with the resource type and the function to get the resource
            config = self._generate_resource_config_for_all_objects_of_a_resource_type(resource_type, api_call)

            print(f'Generating config for {resource_type} at target/{resource_type}.tf...')
            
            with open(f'target/{resource_type}.tf', 'w') as f:
                for resource in config:
                    f.write("resource \"{}\" \"{}\" {{\n".format(resource["type"], resource["name"]))
                    for property, value in resource["properties"].items():
                        f.write("    {} = \"{}\"\n".format(property, value))
                    f.write("}\n\n")
            
            print(f'Generating config for {resource_type} at target/{resource_type}.tf...done')

    def run_terraform_init(self):
        """
        This method runs terraform init in the target directory.
        """
        # Run terraform init
        print("Running terraform init...")
        subprocess.run(["terraform", "-chdir=target", "init"], check=True)
        print("Running terraform init...done")

    def import_resources(self):
        """
        This method imports the resources into the terraform state.
        It uses the self.resource_mapping dictionary to map the resource name to the cloud ID.
        It runs the cli command 'terraform import' for each resource.
        """
        # Delete existing .tfstate file if it exists
        if os.path.exists(self.tfstate_file_path):
            os.remove(self.tfstate_file_path)
            print(f"Deleted existing {self.tfstate_file_path} file.")

        # Import resources into Terraform state
        print("Importing resources into Terraform state...")
        for resource_name, resource_id in self.resource_mapping.items():
            subprocess.run(["terraform", "-chdir=target", "import", resource_name, resource_id], check=True)
        print("Importing resources into Terraform state...done")

    def update_tf_files_with_optional_properties(self):
        """
        This method updates the .tf files with optional properties.
        It uses the .tfstate file to get the optional properties.
        It only updates the properties that are not already in the .tf file.
        It only considers properties that are in the self.valid_properties dictionary.
        """
        # Check if .tfstate file exists
        if not os.path.exists(self.tfstate_file_path):
            print("No .tfstate file found. Run 'import_resources' first.")
            return

        print("Updating .tf files with optional properties...")

        # Load .tfstate file
        with open(self.tfstate_file_path, 'r') as f:
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

                        # Loop through each property in the .tfstate and add it to the .tf file if it doesn't already exist
                        for key, value in instance_attributes.items():
                            if key not in self.valid_properties.get(resource_type, {}).get('optional_properties', []):  # Check if the property is valid
                                continue
                            if isinstance(value, list) and len(value) == 0:  # Skip properties with empty array as value
                                continue
                            if not any(key in line for line in tf_file_content[resource_line_num:resource_end_line_num]):
                                if value is None:
                                    tf_file_content.insert(resource_end_line_num, f'    {key} = null\n')
                                elif isinstance(value, bool):
                                    tf_file_content.insert(resource_end_line_num, f'    {key} = {str(value).lower()}\n')  # no quotes around boolean values
                                elif isinstance(value, list):
                                    tf_file_content.insert(resource_end_line_num, f'    {key} = {value}\n')  # no quotes around array values
                                else:
                                    tf_file_content.insert(resource_end_line_num, f'    {key} = "{value}"\n')
                                resource_end_line_num += 1  # increment the end line num to keep up with the added lines

            with open(tf_file_path, 'w') as f:
                f.writelines(tf_file_content)

        print("Updating .tf files with optional properties...done")