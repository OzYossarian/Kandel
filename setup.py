from setuptools import setup

setup(
    python_requires='>=3.6',
    name='FaultTolerantQPU',
    version='0.1dev',
    packages=['main', 'tests'],
    license='GNU General Public License v3.0',
    long_description=open('README.md').read(),
    install_requires=["numpy"]
)
