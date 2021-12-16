from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
        name='aqmd_lib',
        version="0.0.1",
        description='A Data Analysis Toolbox for Air Quality Modeling Research',
        url='https://github.com/Xander-git/AQMD-Library',
        author='Alexander Nguyen',
        author_email='alxxander.nguyen@gmail.com',
        license='MIT',
        packages=['data_toolkit', 'graph', 'machine_learning', 'util'],
        project_urls={
            'Bug Tracker': 'https://github.com/Xander-git/AQMD-Library/issues'
        },
        classifiers=[
          "Intended Audience :: Data Scientist",
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python :: 3"
        ],
        python_requires='>=3.8',
        package_dir={
            "": 'src'
        }

)
