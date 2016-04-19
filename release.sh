#!/bin/bash
# Push package to PyPI
#
# 1. Bump version in sentrycli.__init__.py
# 2. Commit and push to origin
# 3. ./release.sh

set -e
set -u
VERSION=`./setup.py --version`
echo "Releasing ${VERSION}"
git tag $VERSION || true
git push --tags origin master
python setup.py sdist upload -r pypi
