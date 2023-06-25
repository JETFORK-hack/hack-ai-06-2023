from pydantic import BaseModel


class RemarkWithFileName(BaseModel):
    id: int
    file_id: int
    file_name: str  # new field
    page_num: int
    golden_name: str
    targets: str
    candidate: str
    probability: float
    similarity: float
