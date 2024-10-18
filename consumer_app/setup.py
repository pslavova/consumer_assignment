from setuptools import setup, find_packages

setup(
    name='consumer_app',
    version='0.0.1',
    author_email='petya.slavova@gmail.com',
    packages=find_packages(where='src'),
    package_dir={"":"src"},
    install_requires=[
        'redis',
        'flask',
        'requests',
        'marshmallow'
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'requests-mock'],

    python_requires='>=3.9',
)
