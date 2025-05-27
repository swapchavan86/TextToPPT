# backend/config.py
import os
import logging
from dotenv import load_dotenv

# --- Environment Variable Loading ---
# More robust .env loading
dotenv_path_script_dir = os.path.join(os.path.dirname(__file__), '.env')
dotenv_path_cwd = os.path.join(os.getcwd(), '.env')

if os.path.exists(dotenv_path_script_dir):
    load_dotenv(dotenv_path=dotenv_path_script_dir)
    print(f"INFO: Loaded .env file from script directory: {dotenv_path_script_dir}")
elif os.path.exists(dotenv_path_cwd):
    load_dotenv(dotenv_path=dotenv_path_cwd)
    print(f"INFO: Loaded .env file from current working directory: {dotenv_path_cwd}")
else:
    print("INFO: .env file not found. Relying on system environment variables.")


# --- API Keys ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
# IMAGE_GENERATION_API_KEY = os.getenv("YOUR_IMAGE_API_KEY") # For future use

# --- Logging ---
# Basic logging configuration can be done here or in main.py's startup
# For simplicity, we'll keep the main setup in main.py, but you could move it.
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("app_config") # Use a specific logger name

# --- Styling Constants ---
PROFESSIONAL_COLORS_HEX = {
    "dark_blue": "003366", "medium_blue": "0072C6", "dark_grey": "404040",
    "teal": "008080", "burgundy": "800020", "forest_green": "228B22"
}
PROFESSIONAL_FONT_NAMES = ["Calibri", "Arial", "Tahoma", "Verdana"]
SUBTLE_BACKGROUND_COLORS_HEX = ["F0F8FF", "F5F5F5", "FAF0E6", "E6E6FA", "FFF0F5"]

THEME_STYLES = {
    "technology": {
        "colors": {
            "primary": "003366",    # Dark blue
            "secondary": "0072C6",  # Medium blue
            "accent": "66B2FF",     # Light blue
            "background": {"type": "gradient", "color1": "E0E8F0", "color2": "F0F8FF", "angle": 45}, # Original: F0F8FF
            "text": "333333"         # Dark grey
        },
        "font": "Arial"
    },
    "nature": {
        "colors": {
            "primary": "228B22",    # Forest green
            "secondary": "3CB371",  # Medium sea green
            "accent": "90EE90",     # Light green
            "background": {"type": "gradient", "color1": "E6F5E6", "color2": "F0FFF0", "angle": 45}, # Original: F0FFF0
            "text": "2F4F2F"         # Dark slate gray
        },
        "font": "Verdana"
    },
    "business": {
        "colors": {
            "primary": "404040",    # Dark grey
            "secondary": "808080",  # Grey
            "accent": "D3D3D3",     # Light grey
            "background": {"type": "gradient", "color1": "E8E8E8", "color2": "F5F5F5", "angle": 45}, # Original: F5F5F5
            "text": "000000"         # Black
        },
        "font": "Calibri"
    },
    "education": {
        "colors": {
            "primary": "FF8C00",    # Dark orange
            "secondary": "FFA500",  # Orange
            "accent": "FFD700",     # Gold
            "background": {"type": "gradient", "color1": "FFF5E0", "color2": "FFF8DC", "angle": 45}, # Original: FFF8DC
            "text": "542C06"         # Dark Brown
        },
        "font": "Tahoma"
    },
    "default": { # Fallback theme
        "colors": {
            "primary": "bdc3c7",    # Silver (for titles)
            "secondary": "3498db",  # Peter River blue (accent1)
            "accent": "2980b9",     # Belize Hole blue (accent2)
            "background": {"type": "gradient", "color1": "2c3e50", "color2": "485a6d", "angle": 45}, # Original: 2c3e50
            "text": "ecf0f1"         # Light Grey / Off-white (for body text)
        },
        "font": "Calibri"
    }
}

THEME_KEYWORD_ALIASES = {
    "technology": [
        "ai", "artificial intelligence", "tech", "innovation", "digital", 
        "software", "computer", "robotics", "automation", "future tech",
        "advancements", "transformation", "singularity", "algorithm"
    ],
    "nature": [
        "environment", "eco", "green", "forest", "outdoors", "wildlife", 
        "sustainability", "conservation", "planet", "earth", "natural"
    ],
    "business": [
        "finance", "corporate", "company", "market", "economic", "investment",
        "strategy", "management", "entrepreneur", "commerce", "industry", "reports"
    ],
    "education": [
        "learning", "school", "university", "academic", "study", "teaching",
        "knowledge", "curriculum", "student", "pedagogy"
    ]
    # Add other main themes here if they exist and need aliases,
    # but not for "default" as it's a fallback.
}

# --- Application Settings ---
PPT_OUTPUT_DIR = "generated_files"
PLACEHOLDER_IMAGE_DIR_NAME = "placeholders" # Relative to PPT_OUTPUT_DIR
PLACEHOLDER_IMAGE_FILENAME = "placeholder.png"

# --- CORS Origins ---
# Allow easy configuration of origins via environment variable or defaults
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000").strip()
DEFAULT_ORIGINS = ["http://localhost", "http://localhost:8000"] # Add FastAPI's own port for testing
EFFECTIVE_ORIGINS = list(set(DEFAULT_ORIGINS + ([FRONTEND_URL] if FRONTEND_URL else [])))


if not GOOGLE_API_KEY:
    logger.error("CRITICAL: GOOGLE_API_KEY environment variable not set in config.py. AI features will NOT work.")

# You could add more application-wide configurations here