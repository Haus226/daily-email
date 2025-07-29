from typing import List, TypedDict
import logging
import os

class PaperInfo(TypedDict):
    paper_link: str
    pdf_link: str
    github_link: str | None
    abstract: str
    published_date: str
    star_cnt: str
    upvote_cnt: str
    tags: List[str]
    llm_summary: str
    
def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger with the specified name and logging level.
    
    Args:
        name (str): The name of the logger.
        level (int): The logging level (default is logging.INFO).
    
    Returns:
        logging.Logger: Configured logger instance.
    """

    log_path = os.path.join(f"logs/{name}", ".log")
    handler = logging.FileHandler(log_path, encoding="utf-8")
    formatter = logging.Formatter(
        "%(levelname)-8s %(asctime)s [%(filename)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    # prevent duplicate logs from root logger
    logger.propagate = False  
    return logger