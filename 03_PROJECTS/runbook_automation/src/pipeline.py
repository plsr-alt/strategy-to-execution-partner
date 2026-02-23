import argparse
import logging
import os
from src.ocr_engine import OCREngine
from src.extractor import Extractor
from src.sheets_writer import SheetsWriter
from src.doc_generator import DocGenerator
from src.capturer import Capturer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Runbook Automation POC - Documentation Generator")
    parser.add_argument("--mode", type=str, choices=["extract", "generate"], default="generate", help="Mode: extract data to sheets or generate documentation")
    parser.add_argument("--input", type=str, nargs="+", required=True, help="Path to input image(s)")
    parser.add_argument("--mock", action="store_true", help="Run in mock mode")
    parser.add_argument("--output", type=str, default="outputs/manual.md", help="Output documentation path")
    args = parser.parse_args()

    logger.info(f"Starting pipeline (Mode: {args.mode}, Mock: {args.mock})")

    if args.mode == "generate":
        # 1. Capture (If URLs are provided instead of files)
        image_paths = args.input
        if all(url.startswith("http") for url in args.input):
            capturer = Capturer(use_mock=args.mock)
            # For prototype, we just capture the first URL provided
            image_paths = capturer.capture_aws_console(args.input[0], "data/captures")

        # 2. Generate Documentation
        generator = DocGenerator(use_mock=args.mock)
        documentation = generator.generate_step_description(image_paths)
        
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(documentation)
        
        logger.info(f"Documentation saved to {args.output}")

    else:
        # Old Flow: DATA EXTRACTION
        ocr = OCREngine(use_mock=args.mock)
        ocr_result = ocr.analyze_image(args.input[0])

        extractor = Extractor(use_mock=args.mock)
        field_defs = {"Date": "Extracted date", "Amount": "Total amount"}
        extraction = extractor.extract_fields(ocr_result, field_defs)

        writer = SheetsWriter("MOCK_ID", use_mock=args.mock)
        row = [extraction.items.get(k, "") for k in field_defs.keys()]
        writer.append_row(row)

    logger.info("Pipeline completed successfully")

if __name__ == "__main__":
    main()
