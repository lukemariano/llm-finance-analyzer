import pandas as pd
from groq import Groq
from time import sleep
from typing import List, Optional

import logging
from tqdm import tqdm

from config import Config
from template_manager import TemplateManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExpenseClassifier:
    def __init__(self, config: Config = None, template_manager: TemplateManager = None):
        self.config = config or Config()
        self.template_manager = template_manager or TemplateManager(
            self.config.TEMPLATE_FILE,
            self.config.CATEGORIES_FILE
        )
        self.client = Groq(api_key=self.config.API_KEY)
    
    def classify_single_transaction(self, description: str) -> str:
        """
        Classify a single transaction description using the configured LLM model.
        """

        # Special cases that do not require LLM classification
        if description.lower() == "saldo do dia":
            return "Saldo do dia"
        
        try:
            message_content = self.template_manager.format_message(description)

            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "Você é um analista de dados financeiros e está analisando os extratos bancários de um cliente que é pessoa física."
                    },
                    {
                        "role": "user",
                        "content": message_content
                    }
                ],
                model=self.config.LLM_MODEL,
            )

            category = chat_completion.choices[0].message.content.strip()
            return category
        except Exception as e:
            logger.error(f"Error classifying transaction '{description}': {e}")
            return "Não classificado"
    
    def classify_batch(self, descriptions: List[str]) -> List[str]:
        """
        Classify a batch of transactions with rate limiting control.
        """

        categories = []

        with tqdm(total=len(descriptions), desc="Classifying transactions") as pbar:
            for i, description in enumerate(descriptions):
                if (
                    self.config.USE_RATE_LIMIT 
                    and i > 0
                    and i % self.config.RATE_LIMIT_BATCH_SIZE == 0
                ):
                    logger.info(f"Rate limit reached. Sleeping for {self.config.RATE_LIMIT_SLEEP_TIME} seconds...")
                    sleep(self.config.RATE_LIMIT_SLEEP_TIME)
                
                category = self.classify_single_transaction(description)
                categories.append(category)

                pbar.set_postfix({"Last category": category})
                pbar.update(1)
        return categories
    
    def process_dataframe(self, df: pd.DataFrame, description_column: str = "description") -> pd.DataFrame:
        """Process a DataFrame with expenses classification."""
        if description_column not in df.columns:
            raise ValueError(f"Column '{description_column}' not found in DataFrame.")
        
        logger.info("Starting classification of transactions...")

        descriptions = df[description_column].values
        categories = self.classify_batch(descriptions)

        df_result = df.copy()
        df_result["category"] = categories

        logger.info("Classification completed.")
        return df_result
    
    def save_results(self, df: pd.DataFrame, output_file: str = None):
        """Save the classified DataFrame to a CSV file."""
        output_file = output_file or self.config.OUTPUT_FILE
        df.to_csv(output_file, index=False)
        logger.info(f"Results saved to {output_file}")
    
    def get_classification_summary(self, df: pd.DataFrame) -> pd.DataFrame:
        """Get a summary of classifications."""
        if "category" not in df.columns:
            raise ValueError("DataFrame must contain a 'category' column.")
        
        summary = (
            df
            .groupby("category")
            .agg(
                {
                    "amount": ["count", "sum", "mean"],
                    "date": ["min", "max"]
                }
            )
            .round(2)
        )

        summary.columns = ["Quantity", "Total", "Average", "First_Date", "Last_Date"]
        return summary.sort_values(by="Total", ascending=False)