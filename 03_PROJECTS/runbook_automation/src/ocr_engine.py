import boto3
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class OCREngine:
    def __init__(self, use_mock: bool = False):
        self.use_mock = use_mock
        if not use_mock:
            self.client = boto3.client('textract')

    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze an image using AWS Textract or return dummy data in mock mode.
        """
        if self.use_mock:
            logger.info(f"[MOCK] Skipping AWS Textract for {image_path}")
            return {
                "Blocks": [
                    {"BlockType": "LINE", "Text": "SAMPLE OCR TEXT", "Confidence": 99.0},
                    {"BlockType": "KEY_VALUE_SET", "EntityTypes": ["KEY"], "Text": "Date:"},
                    {"BlockType": "KEY_VALUE_SET", "EntityTypes": ["VALUE"], "Text": "2026-02-23"}
                ]
            }

        logger.info(f"Analyzing image: {image_path}")
        with open(image_path, 'rb') as document:
            image_bytes = document.read()

        response = self.client.analyze_document(
            Document={'Bytes': image_bytes},
            FeatureTypes=['FORMS', 'TABLES']
        )
        return response
