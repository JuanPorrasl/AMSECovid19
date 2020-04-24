import dash
import dash_bootstrap_components as dbc
import dash_auth
import sys
#Initializing our app & calling the external stylesheet
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = 'COVID-19 AMSE Project'
server = app.server
app.config.suppress_callback_exceptions = True

sys.path.append('../')
from confidential.secrets import VALID_USERNAME_PASSWORD_PAIRS

auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)




