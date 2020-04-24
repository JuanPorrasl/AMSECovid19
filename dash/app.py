import os

import dash
import dash_bootstrap_components as dbc
import dash_auth
#import sys


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'COVID-19 AMSE Project'
server = app.server
app.config.suppress_callback_exceptions = True


if os.environ.get('COVID_APP_ENV', 'local') != 'local':
   from confidential.secrets import VALID_USERNAME_PASSWORD_PAIRS
else:
   from local_env import VALID_USERNAME_PASSWORD_PAIRS


auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)

