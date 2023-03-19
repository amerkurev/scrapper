from setuptools import setup

setup(
    name='scrapper',
    packages=['scrapper'],
    include_package_data=True,
    install_requires=[
        'Flask==2.2.3',
        'Jinja2==3.1.2',
        'beautifulsoup4==4.11.2',
        'waitress==2.1.2',
        'validators==0.20.0',
    ],
    # version='0.0.0',
)
