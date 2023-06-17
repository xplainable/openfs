from setuptools import find_packages, setup

exec(open('openfs/_version.py').read())

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("LICENSE", "r") as fh:
    license = fh.read()

setup(
    name='openfs',
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
        'pandas>=1.2.0'
    ],
    extras_require={
        'gui': ['ipywidgets>=8.0.0', 'ipython']
    }
)
