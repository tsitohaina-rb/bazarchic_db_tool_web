"""
Configuration for Cloudinary uploads
"""

import os
import cloudinary
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Cloudinary Configuration
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET')
)

# Upload Settings
CLOUDINARY_FOLDER = "bazarchic_images"  # Default folder in Cloudinary
USE_FILENAME = True  # Use original filename
UNIQUE_FILENAME = False  # Don't add random suffix to filename
