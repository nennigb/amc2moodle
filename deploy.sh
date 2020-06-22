#!/bin/bash

for i in "$@"
do
    case "$i" in
    -i|--install) pip install twine
    ;;
    -t|--test)  pip wheel . -w dist
    twine upload --repository-url https://test.pypi.org/legacy/ dist/amc2moodle*.whl
        ;;
    -d|--deploy)  pip wheel . -w dist
    twine upload --repository-url https://pypi.org/legacy/ dist/amc2moodle*.whl
        ;;
    esac
done

