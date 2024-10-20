# Roamly

Context Aware Intelligent Travel Companion

## Prerequisites

\*\*\_ MUST HAVE PYTHON > 3.11.2

## Clone the project using

> `git clone {project_url}`

## navigate to project directory

> `cd Roamly`

## Create a virtual environment for the project using

> `py -m venv .venv`

## To start the virtual environment

- navigate to .venv/Scripts

  > run `activate.bat` --> Command Prompt

- bash
  > source .venv/Scripts/activate

Then install all the dependencies with the following command

> `pip install -r requirements.txt`

## To run the project on debugging mode

> `py app.py`

## Run with flask command

> `flask run`

## Configuration Setup

To set up your local configuration, follow these steps:

1. **Create a `config.py` file**:

   - Copy the provided `config_template.py` file and rename it to `config.py` in the root of the project directory.
   - This file contains placeholders for sensitive configuration details (e.g., `SECRET_KEY`, `MONGO_URI`).

   Example command:

   ```bash
   cp config_template.py config.py
   ```
