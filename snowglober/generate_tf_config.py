import json
import os

class TerraformConfigGenerator:
    def __init__(self, connector):
        self.connector = connector

    def _generate_warehouse_config(self):
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

    # TODO: Implement more methods like _generate_warehouse_config for other resource types
    # def _generate_user_config(self):
    #     ...

    def write_config_to_file(self):
        # Create target directory if it doesn't exist
        os.makedirs('target', exist_ok=True)

        # List of resource types and corresponding config generation methods
        resources_to_generate = [
            {"resource_type": "warehouse", "generation_method": self._generate_warehouse_config},
            # Add more dictionary entries for other resource types like so:
            # {"resource_type": "user", "generation_method": self._generate_user_config},
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