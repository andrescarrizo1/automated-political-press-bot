from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum

class NewsType(str, Enum):
    OBRA_PUBLICA = "obra_publica"
    EVENTO_CULTURAL = "evento_cultural"
    CONFLICTO_GREMIAL = "conflicto_gremial"
    TURISMO_TEMPORADA = "turismo_temporada"
    GESTION_INSTITUCIONAL = "gestion_institucional"
    SEGURIDAD = "seguridad"
    ECONOMIA_MINERIA = "economia_mineria"
    AMBIENTE_CLIMA = "ambiente_clima"

class NewsItem(BaseModel):
    title: str
    source: str
    date: str
    content: str
    url: str
    client_id: str

class FramingRule(BaseModel):
    news_type: NewsType
    angle: str
    must_include: List[str]
    forbidden_frames: List[str]
    quote_sources: List[str]
    cta: str
    seo_keywords: List[str]

class FramedNews(BaseModel):
    original: NewsItem
    news_type: NewsType
    rule: FramingRule
    entities: Dict[str, str]
    prompt: str
