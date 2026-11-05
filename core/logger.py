"""
Formatted logging utility for WavexOne Automated QA.
Configured for Windows UTF-8 stdout and rotating log files.
"""
import logging
import sys
from pathlib import Path
from config.settings import WavexSettings

# Ensure UTF-8 output on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def setup_logger(name: str = "wavexone_qa") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # Console Handler
    c_handler = logging.StreamHandler(sys.stdout)
    c_handler.setLevel(logging.INFO)
    c_format = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
    c_handler.setFormatter(c_format)
    logger.addHandler(c_handler)

    # File Handler
    log_file = WavexSettings.LOGS_DIR / "wavexone_qa.log"
    f_handler = logging.FileHandler(log_file, encoding="utf-8")
    f_handler.setLevel(logging.DEBUG)
    f_format = logging.Formatter("%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d]: %(message)s")
    f_handler.setFormatter(f_format)
    logger.addHandler(f_handler)

    return logger

logger = setup_logger()
