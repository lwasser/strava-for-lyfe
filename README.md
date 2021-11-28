# Strava for Lyyyyffe
Total geek terrain here

This is a test space that I use to track my strava stats and play with various visualization and
Python development options! Enter at your own risk. :)

### Basic Installation

Clone locally

To run in interactive (development) mode:

`$ pip install -e .`

Play with the notebooks. I'm not sure that i've setup the authentication in a way that others
can use this yet I believe I need to add instructions for setup of your strava app, secret and code.

more to come...  :)


## Requirements

To begin install the environment which is conda-forge channel focused.

`conda env create -f environment.yml`

Then activate the environment: 
`conda activate strava-lyfe`

Optional - install the pre-commit hooks for linting:

`pip install -r requirements.txt`

and then 

`pre-commit install`

Install the Jupyter lab extension to ensure plotly works correctly 

`jupyter labextension install jupyterlab-plotly@4.14.3`

If using JupyterLab, install the plotly extension

`conda install -c conda-forge jupyterlab-plotly-extension`
