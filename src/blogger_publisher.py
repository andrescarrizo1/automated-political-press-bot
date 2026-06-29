import os
import json
import logging
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/blogger"]
TOKEN_PATH = "token_blogger.json"
CREDENTIALS_PATH = "credentials_blogger.json"

logger = logging.getLogger(__name__)

def _get_blogger_service():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())
    return build("blogger", "v3", credentials=creds, cache_discovery=False)

def publicar_en_blogger(titulo, contenido_html, categoria, labels_extra=None, meta_description=None) -> str:
    """Publica contenido en Blogger usando API completa de etiquetas y meta."""
    blog_id = os.environ.get("BLOGGER_BLOG_ID")
    service = _get_blogger_service()

    labels = [categoria, "Malargüe", "Mendoza"] + (labels_extra or [])
    body = {
        "title": titulo,
        "content": contenido_html,
        "labels": labels,
        "customMetaData": meta_description or ""
    }

    response = service.posts().insert(blogId=blog_id, body=body, isDraft=False).execute()
    return response['url']
