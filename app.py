import numpy as np


import flask
import dash
import plotly.graph_objs as go

from instruments import Instrument
import dash_components as dc
import updates

#########################################
# 1. Define the Flask server and Dash app
#########################################
server = flask.Flask(__name__)
app = dash.Dash(
    __name__,
    server=server,
    url_base_pathname='/dash/',  # This ensures Dash app is served at /dash/
    suppress_callback_exceptions=True  # Add this line to suppress callback exceptions
)

#########################################
# 2. Define the Dash app layout
#########################################
app.layout = dc.create_layout()

#########################################
# 3. Register callbacks
#########################################
updates.register_callbacks(app)

#########################################
# 4. Run the Server
#########################################
if __name__ == '__main__':
    app.run_server(
        debug=True,
        port=5000,
        host='0.0.0.0'
    )
