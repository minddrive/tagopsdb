from setuptools import setup, find_packages

# Let's add this later
# long_description = open('README.txt').read()

# Get version of project
execfile('version.py')

setup_args = dict(
    name = 'TagOpsDB Library',
    version = __version__,
    description = 'Python library to interface with TagOps database',
    # long_description = long_description,
    author = 'Kenneth Lareau',
    author_email = 'klareau@tagged.com',
    license = 'Apache License, Version 2.0',
    packages = ['tagopsdb', 'tagopsdb.database', 'tagopsdb.deploy'],
    package_dir = {'' : 'lib/python'},
    scripts = [],
)

if __name__ == '__main__':
    setup(**setup_args)
