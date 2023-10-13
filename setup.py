from setuptools import find_packages,setup

with open("requirements.txt") as f:
    requires = f.read().splitlines()

LONG_DESCRIPTION = "Pending"

setup(
    name='c3-python-sdk',
    version='0.0.1',
    packages=find_packages(),
    description='Python REST API SDK for C3.io Exchange',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url='https://github.com/c3exchange/c3-python-sdk',
    author='C3 Exchange',
    license='Apache 2.0',
    author_email='contact@c3.io',
    install_requires=requires,
    keywords='c3 crypto exchange rest api defi wormhole ethereum eth algorand algo',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)