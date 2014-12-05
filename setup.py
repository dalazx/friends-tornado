from setuptools import setup, find_packages


setup(
    name='friends-tornado',
    version='0.0.1',
    description='Friends Relationship Management Service',
    url='',
    author='Aleksandr Danshyn',
    author_email='dalazx@gmail.com',

    packages=find_packages(),
    install_requires=['tornado', 'tornado-redis'],
    test_suite='friends_tornado.tests'
)
