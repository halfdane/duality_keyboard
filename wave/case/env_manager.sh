#!/bin/bash

VENV_NAME=".venv"
REQUIREMENTS="requirements.txt"

function create_env() {
    echo "Creating virtual environment: $VENV_NAME"
    python3 -m venv $VENV_NAME
    source $VENV_NAME/bin/activate
    pip install --upgrade pip
    pip install -r $REQUIREMENTS
    
    # Ensure ipykernel is installed and properly registered
    pip install ipykernel
    python -m ipykernel install --user --name=wave_case --display-name="Wave Case Python"
    
    # Check installations
    echo "===== Python version ====="
    python --version
    echo "===== Installed packages ====="
    pip list | grep -E "notebook|jupyter|ipykernel|build123d"
    
    echo "Environment created and dependencies installed"
}

function activate_env() {
    echo "Activating virtual environment"
    source $VENV_NAME/bin/activate
}

function deactivate_env() {
    echo "Deactivating virtual environment"
    deactivate
}

function destroy_env() {
    echo "Removing virtual environment"
    rm -rf $VENV_NAME
    jupyter kernelspec remove wave_case -y 2>/dev/null || true
    echo "Environment removed"
}

function start_notebook() {
    activate_env
    # Check Python executable and environment
    which python
    echo "PYTHONPATH: $PYTHONPATH"
    
    # Make sure the kernel is available and show registered kernels
    python -m ipykernel install --user --name=wave_case --display-name="Wave Case Python"
    jupyter kernelspec list
    
    # Start notebook with more verbose output
    python -m notebook --debug
}

case "$1" in
    create)
        create_env
        ;;
    activate)
        activate_env
        ;;
    deactivate)
        deactivate_env
        ;;
    destroy)
        destroy_env
        ;;
    notebook)
        start_notebook
        ;;
    *)
        echo "Usage: $0 {create|activate|deactivate|destroy|notebook}"
        exit 1
esac

echo "Done"
