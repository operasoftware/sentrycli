#!/bin/bash
# Push package to PyPI

set -e
set -u
VERSION=`./setup.py --version`
echo "Releasing ${VERSION}"
git tag $VERSION
git push --tags origin master
python setup.py sdist upload -r pypi
