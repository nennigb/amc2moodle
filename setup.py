from setuptools import setup, find_packages
import subprocess
import os

with open("README.md", "r") as fh:
    long_description = fh.read()

def get_git_revision_short_hash():
    """determines the git revision; only works if the packages was checked
    out using git"""
    ghash = subprocess.check_output(
        ['git', 'describe', '--always'], cwd=os.getcwd())
    try:
        # ghash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'])
        ghash = subprocess.check_output(
            ['git', 'describe', '--always'], cwd=os.getcwd())

        ghash = ghash.decode('utf-8').rstrip()
    except:
        # git isn't installed
        ghash = 'no.checksum.error'
    return '%s' % ghash

__version__ = get_git_revision_short_hash()
print(__version__)

setup(
    name="amc2moodle", # Replace with your own username
    version=__version__,
    author="B. Nennig",
    author_email="benoit.nennig@supmeca.fr",
    description="A tool to convert automultiplechoice quizz to moodle questions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nennigb/amc2moodle",
    zip_safe=False,
    packages=find_packages(),
    package_data={'': ['*.xslt']},
    scripts=['amc2moodle.py'],
    # package_data={'amc2moodle': ['src/*']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU GPL 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)