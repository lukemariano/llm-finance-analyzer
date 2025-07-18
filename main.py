import argparse
import sys
from pathlib import Path

from pdf_to_pandas import load_all_itau_statements
from config import Config
from template_manager import TemplateManager
from expense_classifier import ExpenseClassifier

def main():
    parser = argparse.ArgumentParser(
        description="Classify bank expenses using LLMs.",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--extratos-dir",
        type=Path,
        help="Directory containing the statements (default: value from .env)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        help="Output file (default: value from .env)"
    )
    
    parser.add_argument(
        "--template",
        type=str,
        help="Custom template file"
    )
    
    parser.add_argument(
        "--categories",
        type=str,
        help="Custom categories file"
    )
    
    parser.add_argument(
        "--no-rate-limit",
        action="store_true",
        help="Disable rate limiting (for paid accounts)"
    )
    
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Show classification summary"
    )
    
    parser.add_argument(
        "--validate-config",
        action="store_true",
        help="Only validate the configuration and exit"
    )
    
    args = parser.parse_args()

    try:
        config = Config()

        if args.extratos_dir:
            config.EXTRATOS_DIR = args.extratos_dir
        if args.output:
            config.OUTPUT_FILE = args.output
        if args.no_rate_limit:
            config.USE_RATE_LIMIT = False
        
        config.validate()

        if args.validate_config:
            print("✅ Valid configuration!")
            print(f"API Key: {'✅ Defined' if config.API_KEY else '❌ Not defined'}")
            print(f"Model: {config.LLM_MODEL}")
            print(f"Rate Limiting: {'✅ Enabled' if config.USE_RATE_LIMIT else '❌ Disabled'}")
            print(f"Statements Directory: {config.EXTRATOS_DIR}")
            return
        
        print(f"Processing statements in: {config.EXTRATOS_DIR}...")
        df_statements = load_all_itau_statements(config.EXTRATOS_DIR)
        print(f"Total transactions loaded: {len(df_statements)}")

        template_manager = TemplateManager(
            args.template or config.TEMPLATE_FILE,
            args.categories or config.CATEGORIES_FILE,
        )

        classifier = ExpenseClassifier(
            config=config,
            template_manager=template_manager
        )

        print("Initiating classification...")
        df_result = classifier.process_dataframe(df_statements)

        classifier.save_results(df_result, config.OUTPUT_FILE)

        if args.summary:
            print("\nClassification Summary:")
            summary = classifier.get_classification_summary(df_result)
            print(summary.to_string())
        
        print("Classification completed successfully! File saved to:", config.OUTPUT_FILE)

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()