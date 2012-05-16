from setuptools import setup, find_packages

# Let's add this later
# long_description = open('README.txt').read()

setup_args = dict(
    name = 'TagOpsDB Library',
    version = '1.0.0',
    description = 'Python library to interface with TagOps database',
    # long_description = long_description,
    author = 'Kenneth Lareau',
    author_email = 'klareau@tagged.com',
    license = 'MIT',
    packages = ['tagopsdb'],
    package_dir = {'' : 'lib/python'},
    scripts = [],
)

if __name__ == '__main__':
    setup(**setup_args)