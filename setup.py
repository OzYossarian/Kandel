from setuptools import setup, find_packages

setup(
    python_requires='>=3.6',
    name='Kandel',
    version='0.1dev',
    packages=find_packages(where='main'),
    license='GNU General Public License v3.0',
    long_description=open('README.md').read(),
    install_requires=["numpy"]
)
