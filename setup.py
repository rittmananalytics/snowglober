from setuptools import setup, find_packages

setup(
    name='snowglober',
    version='0.3.0',
    author='Amir Jaber',
    author_email='amir@rittmananalytics.com',
    install_requires=[
        'pandas',
        'sqlalchemy',
        'snowflake-connector-python',
        'python-dotenv',
        # 'terraform', # manually install terraform, not yet available on PyPi
    ],
    url='https://github.com/rittmananalytics/snowglober',
    description='A Python package for exporting Snowflake resources using Terraform',
    long_description=open('README.md').read(),  # Get long description from the README file
    long_description_content_type='text/markdown',  # The type of content in long_description
)