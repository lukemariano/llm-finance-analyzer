import re
import pandas as pd
import pdfplumber
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

def extract_itau_statement(pdf_path: Path) -> pd.DataFrame:
    """
    Extracts Itaú statement data from a PDF and returns a pandas DataFrame.

    Args:
    pdf_path: Path to the statement's PDF file

    Returns:
    DataFrame with columns: date, description, amount, balance
    """
    transactions = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if not text:
                continue
                
            lines = text.split('\n')
            transactions.extend(_parse_lines(lines))
    
    if not transactions:
        print(f"No transactions found in {pdf_path.name}")
        return pd.DataFrame(columns=["date", "description", "amount", "balance"])
    
    df = pd.DataFrame(transactions)
    
    df_clean = _clean_data(df)

    print(f"Extracted {len(df_clean)} transactions from {pdf_path.name}")
    return df_clean

def _parse_lines(lines: List[str]) -> List[Dict]:
    """
    Analyzes lines of extracted text and identifies transactions.
    """
    transactions = []
    
    date_pattern = r'(\d{2}/\d{2}/\d{4})'
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        date_match = re.match(date_pattern, line)
        if not date_match:
            continue
            
        date_str = date_match.group(1)
        remaining_text = line[len(date_str):].strip()
        
        amount, balance = _extract_monetary_values(remaining_text)
        
        description = _extract_description(remaining_text)
        
        if amount is None and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            next_amount, next_balance = _extract_monetary_values(next_line)
            if next_amount is not None:
                amount = next_amount
                balance = next_balance if next_balance is not None else balance
        
        transaction = {
            'date': date_str,
            'description': description,
            'amount': amount,
            'balance': balance
        }
        transactions.append(transaction)
    
    return transactions

def _extract_monetary_values(text: str) -> tuple[Optional[float], Optional[float]]:
    """
    Extracts monetary values from a string.
    Returns (transaction_value, balance) or (None, None) if not found.
    """
    # Standards for Brazilian monetary values
    # Examples: -2,985.00 -8.00 17,398.68
    money_pattern = r'(-?\d{1,3}(?:\.\d{3})*,\d{2})'
    
    matches = re.findall(money_pattern, text)
    
    if not matches:
        return None, None
    
    values = []
    for match in matches:
        clean_value = match.replace('.', '').replace(',', '.')
        values.append(float(clean_value))
    
    if len(values) == 1:
        if values[0] < 0:
            return values[0], None
        else:
            if any(word in text.upper() for word in ['SALDO', 'DISPONÍVEL', 'TOTAL']):
                return None, values[0]
            else:
                return values[0], None
    elif len(values) == 2:
        return values[0], values[1]
    else:
        return values[-2], values[-1]

def _extract_description(text: str) -> str:
    """
    Extracts the transaction description removing monetary values.
    """
    money_pattern = r'(-?\d{1,3}(?:\.\d{3})*,\d{2})'
    description = re.sub(money_pattern, '', text)
    
    description = re.sub(r'\s+', ' ', description).strip()
    
    return description

def _clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and formats the DataFrame data.
    """
    if df.empty:
        return df
    
    df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y', errors='coerce')
    df = df.dropna(subset=['date'])
    df['amount'] = df['amount'].fillna(0)
    df['balance'] = df['balance'].fillna(0)
    df = df[~((df['amount'] == 0) & (df['balance'] == 0))]
    df['description'] = df['description'].str.strip()
    df = df[df['description'] != '']
    df = df.sort_values('date').reset_index(drop=True)
    
    return df

def load_all_itau_statements(folder_path: Path) -> pd.DataFrame:
    """
    Loads and processes all PDF statements in a folder.

    Args:
    folder_path: Path to the folder with the PDFs

    Returns:
    Consolidated DataFrame with all transactions
    """
    pdf_paths = list(folder_path.glob("*.pdf"))
    
    if not pdf_paths:
        print(f"No files found in {folder_path}")
        return pd.DataFrame(columns=["date", "description", "amount", "balance"])
    
    dfs = []
    for pdf_path in pdf_paths:
        try:
            df = extract_itau_statement(pdf_path)
            if not df.empty:
                dfs.append(df)
        except Exception as e:
            print(f"Error processing {pdf_path.name}: {e}")

    if not dfs:
        return pd.DataFrame(columns=["date", "description", "amount", "balance"])

    df_all = pd.concat(dfs, ignore_index=True)
    df_unique = df_all.drop_duplicates().sort_values('date').reset_index(drop=True)

    print(f"Total unique transactions: {len(df_unique)}")
    return df_unique

# Function for analysis and debugging
def analyze_pdf_structure(pdf_path: Path, max_lines: int = 50):
    """
    Auxiliary function to analyze the PDF structure and debug issues.
    """
    print(f"\n=== Analyzing file: {pdf_path.name} ===")
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            print(f"\n--- Page {page_num + 1} ---")
            text = page.extract_text()
            if text:
                lines = text.split('\n')[:max_lines]
                for i, line in enumerate(lines, 1):
                    print(f"{i:2d}: {line}")
            else:
                print("No text extracted")
