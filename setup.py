from setuptools import setup

setup(
    name='pymitter',
    version='0.1.0',
    description='IPC over ZMQ, made easy',
    author='Alexander Rowe',
    author_email='alexrowe707@gmail.com',
    python_requires='>=3.6.0',
    url='https://github.com/aprowe/pymitter',
    packages=[
        'pymitter'
    ],
    install_requires=[
        'PyDispatcher',
        'pyzmq',
    ],
    license='MIT',
)
