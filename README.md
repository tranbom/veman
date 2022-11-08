# veman

veman is a lightweight virtual environment manager using venv.
With veman it is easier to manage multiple environments.

Note: veman is under active development and currently supports Bash in Linux & macOS.

Note for macOS: veman currently only sources ~/.bashrc when activating a venv.

## Installation

Install via pip:
`pip install veman`

### Dependencies

- Python >=3.9
- venv

## Usage

### Create a new virtual environment

`veman create` or
`veman create <environment-name>`

Example:
`veman create djangoenv`


### Activate a virtual environment

`veman activate` or
`veman activate <environment-name>`

Example:
`veman activate djangoenv`


### Deactivate a virtual environment

`deactivate` (inside an active venv)


### List created virtual environments

`veman list`


### Delete a virtual environment

`veman delete` or `veman delete <environment-name>`

Example: `veman delete djangoenv`


### Create and activate a temporary environment

Create a temporary environment which will be deleted immediately when
deactivating the environment.

`veman temp`

To exit & delete the temporary environment type `deactivate`
