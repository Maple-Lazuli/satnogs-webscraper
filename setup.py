from setuptools import setup

VERSION = '1.3.3'
DESCRIPTION = 'Scrape SATNOGS data into a pandas dataframe'
LONG_DESCRIPTION = 'A webscraper to pull multiple satnogs observations into a single pandas dataframe'

setup(
    name="satnogs_webscraper",
    version=VERSION,
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    author="Ada L",
    author_email="the.nostra.tymus@gmail.com",
    license='MIT',
    packages=['satnogs_webscraper'],
    install_requires=[
        'pillow',
        'numpy',
        'requests',
        'bs4',
        'html5lib',
        'pandas',
        'dask[complete]'
    ],
    keywords='satellite satnogs',
    classifiers= [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        'License :: OSI Approved :: MIT License',
        "Programming Language :: Python :: 3",
    ]
)