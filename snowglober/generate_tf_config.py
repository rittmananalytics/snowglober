import json
import os

class TerraformConfigGenerator:
    def __init__(self, connector):
        self.connector = connector

    def _generate_config(self):
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
        return {"resource": resources}

    def generate(self):
        config = self._generate_config()

        os.makedirs('target', exist_ok=True)

        with open('target/warehouse.tf', 'w') as f:
            for resource in config["resource"]:
                f.write("resource \"{}\" \"{}\" {{\n".format(resource["type"], resource["name"]))
                for property, value in resource["properties"].items():
                    f.write("    {} = \"{}\"\n".format(property, value))
                f.write("}\n\n")