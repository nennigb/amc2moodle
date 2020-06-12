from setuptools import setup, find_packages
import subprocess
import os
import shutil


with open("README.md", "r") as fh:
    long_description = fh.read()

# if people don't have git
# def get_git_revision_short_hash():
#     """determines the git revision; only works if the packages was checked
#     out using git"""
#     ghash = subprocess.check_output(
#         ['git', 'describe', '--always'], cwd=os.getcwd())
#     try:
#         # ghash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'])
#         ghash = subprocess.check_output(
#             ['git', 'describe', '--always'], cwd=os.getcwd())

#         ghash = ghash.decode('utf-8').rstrip()
#     except:
#         # git isn't installed
#         ghash = 'no.checksum.error'
#     return '%s' % ghash

def version():
    """ Get version from __init__.py."""
    v = None
    with open(os.path.join('./amc2moodle', '__init__.py')) as f:
        for line in f:
            if line.startswith('__version__'):
                v = line.replace("'", '').split()[-1]
                break
        return v



this_version = version()
print('version:', this_version)


setup(
    name="amc2moodle", # Replace with your own username
    version=this_version,
    author="B. Nennig, L. Laurent",
    author_email="benoit.nennig@supmeca.fr",
    description="A tool to convert automultiplechoice quizz to moodle questions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nennigb/amc2moodle",
    zip_safe=False,
    packages=['amc2moodle','amc2moodle.amc2moodle', 'amc2moodle.moodle2amc'],
    include_package_data=True,
    scripts=['amc2moodle/amc2moodle/bin/amc2moodle',
             'amc2moodle/moodle2amc/bin/moodle2amc'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'wand>=0.5.9',
        'lxml>=3.5.0',
        'wheel>=0.29.0'
    ],
    python_requires='>=3.5'
)