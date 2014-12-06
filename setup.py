from setuptools import setup, find_packages


setup(
    name='friends-tornado',
    version='0.0.1',
    description='Friends Relationship Management Service',
    url='https://github.com/dalazx/friends-tornado',
    author='Aleksandr Danshyn',
    author_email='dalazx@gmail.com',

    packages=find_packages(),
    install_requires=['tornado-redis', 'tornado'],
    test_suite='friends_tornado.tests'
)
