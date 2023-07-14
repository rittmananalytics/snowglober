import json
import os

class TerraformConfigGenerator:
    def __init__(self, connector):
        self.connector = connector

    def _generate_databases_config(self):
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

    def _generate_roles_config(self):
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

    def _generate_users_config(self):
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


    def _generate_warehouses_config(self):
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
                    "auto_suspend_minutes": warehouse['auto_suspend'],
                    "auto_resume": warehouse['auto_resume'].lower(),
                    "initially_suspended": warehouse['state'].upper() == 'SUSPENDED',
                    "scaling_policy": warehouse['scaling_policy'],
                    "min_cluster_count": warehouse['min_cluster_count'],
                    "max_cluster_count": warehouse['max_cluster_count']
                }
            }
            resources.append(resource)
        return resources

    def write_configs_to_files(self):
        # Create target directory if it doesn't exist
        os.makedirs('target', exist_ok=True)

        # List of resource types and corresponding config generation methods
        resources_to_generate = [
            {"resource_type": "databases", "generation_method": self._generate_databases_config},
            {"resource_type": "roles", "generation_method": self._generate_roles_config},
            {"resource_type": "users", "generation_method": self._generate_users_config},
            {"resource_type": "warehouses", "generation_method": self._generate_warehouses_config},
        ]

        # Generate config for each resource type and write to file
        for resource_info in resources_to_generate:
            config = resource_info["generation_method"]()
            with open(f'target/{resource_info["resource_type"]}.tf', 'w') as f:
                for resource in config:
                    f.write("resource \"{}\" \"{}\" {{\n".format(resource["type"], resource["name"]))
                    for property, value in resource["properties"].items():
                        f.write("    {} = \"{}\"\n".format(property, value))
                    f.write("}\n\n")