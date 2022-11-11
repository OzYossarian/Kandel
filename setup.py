from setuptools import setup

setup(
    python_requires='>=3.9',
    name='Kandel',
    version='0.2dev',
    packages=['main', 'tests'],
    license='GNU General Public License v3.0',
    long_description=open('README.md').read(),
    install_requires=["numpy"]
)
