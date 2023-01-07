#!/bin/bash
# Deploy amc2moodle weel to pypi server.

# wheel path
WHEEL_DIR=$(pwd)/dist

function wheel()
{
    # Build and test wheel in an venv to check if all required files are present in
    # the wheel.
    # Clean-up previous version
    rm  $WHEEL_DIR/amc2moodle*.whl
    pip3 wheel . -w dist
    # Setup venv
    TEMP_DIR=$(mktemp -d)
    python3 -m venv $TEMP_DIR
    source $TEMP_DIR/bin/activate
    # Change dir to test really wheel file and not the repo files
    cd $TEMP_DIR
    # Install the wheel
    pip3 install $WHEEL_DIR/amc2moodle*.whl
    # Run all tests
    python3 -m amc2moodle.amc2moodle.test && python -m amc2moodle.moodle2amc.test && python -m amc2moodle.utils.test
    SUCCESS=$?
    # Clean-up tmp directory
    cd $WHEEL_DIR
    trap 'rm -rf "$TEMP_DIR"' EXIT
    if [ $SUCCESS -eq 0 ]
    then
        echo "Ready for uploading :" $(ls $WHEEL_DIR/amc2moodle*.whl)
        return 0
    else
        echo "Test failed. Stop deployment." >&2
        return 1
    fi
}

# Main deployment script
for i in "$@"
do
    case "$i" in
    -i|--install) pip install -e twine
    ;;
    -t|--test)
    wheel && twine upload --verbose -r testpypi $WHEEL_DIR/amc2moodle*.whl
    ;;
    -d|--deploy)
    wheel && twine upload --verbose $WHEEL_DIR/amc2moodle*.whl
    ;;
    esac
done
