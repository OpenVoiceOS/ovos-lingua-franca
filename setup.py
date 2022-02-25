import os
from distutils.command.install import install

import pip
from setuptools import setup

BASEDIR = os.path.abspath(os.path.dirname(__file__))


class CustomInstall(install):
    """Custom handler for the 'install' command."""

    def run(self):
        # uninstall lingua_franca
        # the whole purpose of this package is to replace it
        pip.main(["uninstall", "lingua_franca", "-y"])
        super().run()


def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths


def required(requirements_file):
    """ Read requirements file and remove comments and empty lines. """
    with open(os.path.join(os.path.dirname(__file__), requirements_file),
              'r') as f:
        requirements = f.read().splitlines()
        return [pkg for pkg in requirements
                if pkg.strip() and not pkg.startswith("#")]


def get_version():
    """ Find the version of the package"""
    version = None
    version_file = os.path.join(BASEDIR, 'lingua_franca', 'version.py')
    major, minor, build, alpha = (None, None, None, None)
    with open(version_file) as f:
        for line in f:
            if 'VERSION_MAJOR' in line:
                major = line.split('=')[1].strip()
            elif 'VERSION_MINOR' in line:
                minor = line.split('=')[1].strip()
            elif 'VERSION_BUILD' in line:
                build = line.split('=')[1].strip()
            elif 'VERSION_ALPHA' in line:
                alpha = line.split('=')[1].strip()

            if ((major and minor and build and alpha) or
                    '# END_VERSION_BLOCK' in line):
                break
    version = f"{major}.{minor}.{build}"
    if alpha and int(alpha) > 0:
        version += f"a{alpha}"
    return version


extra_files = package_files('lingua_franca')

with open("readme.md", "r") as fh:
    long_description = fh.read()

setup(
    name='ovos-lingua-franca',
    version=get_version(),
    packages=['lingua_franca', 'lingua_franca.lang'],
    cmdclass={'install': CustomInstall},
    url='https://github.com/OpenVoiceOS/ovos-lingua-franca',
    license='Apache2.0',
    package_data={'': extra_files},
    include_package_data=True,
    install_requires=required('requirements/requirements.txt'),
    author='Mycroft AI / OVOS',
    author_email='jarbasai@mailfence.com',
    description='OpenVoiceOS\'s multilingual text parsing and formatting library',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Text Processing :: Linguistic',
        'License :: OSI Approved :: Apache Software License',

        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
