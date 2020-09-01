
# Import required libraries
import os
from random import randint


import flask
import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html


# Setup the app
# Make sure not to change this file name or the variable names below,
# the template is configured to execute 'server' on 'app.py'
server = flask.Flask(__name__)
server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))
app = dash.Dash(__name__, server=server)


# Put your Dash code here
app.layout = html.H1('Hello World')

# Run the Dash app
if __name__ == '__main__':
    app.server.run(debug=True, threaded=True)