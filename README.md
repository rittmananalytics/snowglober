Project curator: Amir Jaber ( [github](https://github.com/Terroface), [linkedin](https://www.linkedin.com/in/amirjaber/), email: amir@rittmananalytics.com )

# snowglober
Inspired by the Medium article [Terraforming Snowflake (the Easy Way)](https://medium.com/opendoor-labs/terraforming-snowflake-the-easy-way-a87c2750531b)

This package is a WORK IN PROGRESS. It aims to automate migration of Snowflake instances to Terraform by performing the following tasks:
1. extract all **objects** in **Snowflake** which map to a **Terraform** `resource`.
2. create terraform files with resources made to map to each live object.
# Usage
## environment variables in `.tfvars` 
Snowglober automates the creation of the `terraform.tfvars` file, which is used by Terraform for variable definitions. It generates this file using your existing environment variables. If a variable already exists in `terraform.tfvars`, Snowglober will not overwrite it.


1. Ensure your environment variables match (case-insensitively) with the variables listed in the project's [Environment Variables](#environment-variables) section.

2. Run Snowglober. It creates the `terraform.tfvars` file based on your environment variables.

3. Run your usual Terraform commands. The `terraform.tfvars` file is automatically included in these commands, for example, when you run `terraform apply`.


# Dev
This package is open source in nature, under the MIT license. Anyone who wants to contribute is free to do so, just reach out!
## Install in dev mode
```bash
pip install -e /path/to/snowglober/   
```

## Environment variables

`.env` file at top of repo:
```bash
SNOWFLAKE_USERNAME="<value>"
SNOWFLAKE_PASSWORD="<value>"
SNOWFLAKE_ACCOUNT="<value>"
SNOWFLAKE_WAREHOUSE="<value>"
SNOWFLAKE_DATABASE="<value>"
SNOWFLAKE_SCHEMA="<value>"
SNOWFLAKE_ROLE="<value>"
```

## Recommended `.gitignore`
```.gitignore
*.egg-info*
.env*
.venv*
__pycache__/
terraform.tfvars
.terraform*
```

## Run
To run the code, run
```bash
python snowglober/main.py
```
## Unit tests
To test the code, run

```bash
python tests/test_snowflake_connector.py
```