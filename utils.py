from typing import List, TypedDict

class PaperInfo(TypedDict):
    paper_link: str
    pdf_link: str
    github_link: str | None
    abstract: str
    published_date: str
    tags: List[str]