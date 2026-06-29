from pydantic import BaseModel
from typing import List, Optional

class ClientConfig(BaseModel):
    client_id: str
    rol_municipal: str
    personas_protegidas: List[str]
    personas_objetivo: List[str]
    temas_vetar: List[str]
    temas_amplificar: List[str]
    # Aquí irían más configuraciones como URLs, credenciales, etc.
