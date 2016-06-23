from setuptools import setup

# Importing the "multiprocessing" module is required for the "nose.collector".
# See also: http://bugs.python.org/issue15881#msg170215
try:
    import multiprocessing
except ImportError:
    pass

# Define the test runner.
# See also:
# http://fgimian.github.io/blog/2014/04/27/running-nose-tests-with-plugins-using-the-python-setuptools-test-command/
from setuptools.command.test import test as TestCommand
class NoseTestCommand(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True
    def run_tests(self):
        # Run nose ensuring that argv simulates running nosetests directly.
        import nose
        nose.run_exit(argv=['nosetests'])

version = "0.4.0"
readme = open('README.rst').read()


setup(name="jicagile",
      packages=["jicagile"],
      package_data={"jicagile": ["templates/*"]},
      version=version,
      description="Lighweight command line tool for agile project management",
      long_description=readme,
      author='Tjelvar Olsson',
      author_email = 'tjelvar.olsson@jic.ac.uk',
      entry_points = {
        "console_scripts": [
            "agl=jicagile.cli:main",
        ],
      },
      url = 'https://github.com/JIC-CSB/jicagile',
      download_url = 'https://github.com/JIC-CSB/jicagile/tarball/{}'.format(version),
      license='MIT',
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
      ],
      keywords = ['agile', 'project', 'management'],
      cmdclass={"test": NoseTestCommand},
      install_requires=["pyyaml", "python-slugify", "jinja2", "colorama", "termcolor"],
      tests_require=["nose", "coverage"],
)
