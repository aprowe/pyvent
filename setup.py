from setuptools import setup

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='pyvent',
    version='0.1.0',
    description='IPC over ZMQ, made easy',
    long_description=long_description,
    author='Alexander Rowe',
    author_email='alexrowe707@gmail.com',
    python_requires='>=3.6.0',
    url='https://github.com/aprowe/pyvent',
    packages=[
        'pyvent'
    ],
    install_requires=[
        'PyDispatcher',
        'pyzmq',
    ],
    license='MIT',
)
