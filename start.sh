#!/bin/sh

echo 'Creating python virtual environment ".venv"'
python3 -m venv .venv

echo ""
echo "Restoring backend python packages"
echo ""

./.venv/bin/python -m pip install --no-cache-dir -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Failed to restore backend python packages"
    exit $?
fi


echo ""
echo "Starting evals"
echo ""

cd evals

../.venv/bin/python eval_test.py
if [ $? -ne 0 ]; then
    echo "Failed to start evals"
    exit $?
fi
