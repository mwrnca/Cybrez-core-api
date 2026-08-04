from pydantic import BaseModel


class SearchResult(BaseModel):
    type: str
    public_id: str
    title: str
    subtitle: str
    url: str