from setuptools import find_packages, setup

exec(open('featurestore/_version.py').read())

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("LICENCE", "r") as fh:
    license = fh.read()

setup(
    name='featurestore',
    packages=find_packages(),
    version=__version__,
    description='An S3 feature store client for data pipelines.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='xplainable pty ltd',
    author_email="contact@xplainable.io",
    license=license,
    install_requires=[
        'boto3>=1.26.154',
        'botocore>=1.29.154',
        'ipython>=8.14.0',
        'ipywidgets>=8.0.0',
        'pandas>=1.2.0'
    ]
)
