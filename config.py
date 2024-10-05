from kinde_sdk.kinde_api_client import GrantType
import os


SITE_HOST = "localhost"
SITE_PORT = "5000"
SITE_URL = f"http://{SITE_HOST}:{SITE_PORT}"
GRANT_TYPE = GrantType.AUTHORIZATION_CODE_WITH_PKCE
CODE_VERIFIER = "joasd923nsad09823noaguesr9u3qtewrnaio90eutgersgdsfg" # A suitably long string > 43 chars
TEMPLATES_AUTO_RELOAD = True
SESSION_TYPE = "filesystem"
SESSION_PERMANENT = False
SECRET_KEY = "joasd923nsad09823noaguesr9u3qtewrnaio90eutgersgdsfgs" # Secret used for session management
MGMT_API_CLIENT_ID=""
MGMT_API_CLIENT_SECRET=""

KINDE_ISSUER_URL = "https://2024knighthacks.kinde.com"
KINDE_CALLBACK_URL = "http://localhost:5000/api/auth/kinde_callback"
LOGOUT_REDIRECT_URL = "http://localhost:5000"
CLIENT_ID = "1e6a29e092834b2183e0b531b2de63b5"
CLIENT_SECRET = "7IFpdQbbyvA5Eyd9BzlsWenbyiXVa1ZkFdizdNQjEmHZcP5cJaSq"

MIDNIGHT_API_KEY = os.getenv("MIDNIGHT_API_KEY")
MIDNIGHT_API_SECRET = os.getenv("MIDNIGHT_API_SECRET")
