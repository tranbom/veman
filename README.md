# veman

veman is a lightweight virtual environment manager for python meant 
to simplify working with venv.

Note: veman currently only supports Linux & bash

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

`veman activate <environment-name>`

Example:
`veman activate djangoenv`

It is also possible to activate by choosing venv from a list:
`veman activate`


### Deactivate a virtual environment

`deactivate` (inside an active venv)

### List created virtual environments

`veman list`

### Delete a virtual environment

`veman delete` or veman delete <environment-name>
