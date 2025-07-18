from pathlib import Path
import json
from typing import Dict, List

class TemplateManager:
    def __init__(self, template_file: str = None, categories_file: str = None):
        self.template_file = template_file
        self.categories_file = categories_file
        self._template = None
        self._categories = None
        self._category_rules = None

    
    def load_template(self) -> str:
        """Load the template from the specified file."""
        if self._template is None:
            if self.template_file and Path(self.template_file).exists():
                with open(self.template_file, "r", encoding="utf-8") as f:
                    self._template = f.read()
            else:
                self._template = self._get_default_template()
        return self._template
    
    def load_categories(self) -> List[str]:
        """Load categories from the specified file."""
        if self._categories is None:
            if self.categories_file and Path(self.categories_file).exists():
                with open(self.categories_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._categories = data.get("categories", [])
                    self._category_rules = data.get("rules", {})
            else:
                self._categories = self._get_default_categories()
                self._category_rules = self._get_default_rules()
        return self._categories
    
    def get_category_rules(self) -> Dict:
        """Get the rules for each category."""
        if self._category_rules is None:
            _ = self.load_categories()
        return self._category_rules or {}
    
    def format_message(self, description: str) -> str:
        """Format the message using transaction description"""
        template = self.load_template()
        categories = self.load_categories()
        category_rules = self.get_category_rules()

        categories_text = ""
        for category in categories:
            categories_text += f"- {category}"
            if category in category_rules:
                rules = category_rules[category]
                examples = rules.get("examples", [])
                keywords = rules.get("keywords", [])

                if examples or keywords:
                    categories_text += ". "
                    if examples:
                        categories_text += f"Examples: {', '.join(examples)}"
                    if keywords:
                        categories_text += f" Keywords: {', '.join(keywords)}"
            categories_text += "\n"

        return template.format(
            categories=categories_text.strip(),
            description=description
        )


    def _get_default_template(self) -> str:
        """Return the default template."""
        return """
Você é um analista de dados financeiros e está analisando os extratos bancários de um cliente que é pessoa física.
Seu trabalho é identificar uma categoria de gasto com base na descrição da transação.

O output esperado deve ser uma única string que represente a categoria do gasto informado com base na descrição da transação.

Escolha uma das seguintes categorias:
{categories}

Escolha uma das categorias acima e retorne apenas a categoria escolhida.

Dito isso, analise a seguinte transação e retorne a categoria correspondente:
{description}

Responda apenas com a categoria escolhida, sem explicações adicionais. O output deve ser uma única string representando a categoria do gasto.
Se tiver dúvida em alguma classificação, escolha a que se adequa melhor semanticamente.
"""

    def _get_default_categories(self) -> List[str]:
        """List of default categories."""
        return [
            "Alimentação",
            "Deliveries",
            "Transporte",
            "Moradia",
            "Saúde",
            "Mercado",
            "Educação",
            "Streaming",
            "Compras",
            "Lazer",
            "Transferências para terceiros",
            "Barbearia",
        ]

    def _get_default_rules(self) -> Dict:
        """Standard rules for each category."""
        return {
            "Alimentação": {
                "examples": ["121 SMART", "OKEO SAYURI"],
                "keywords": ["restaurante", "lanchonete"]
            },
            "Deliveries": {
                "examples": ["PAY IFD", "IFOOD"],
                "keywords": ["delivery", "entrega"]
            },
            "Transporte": {
                "examples": ["AUTO POSTO"],
                "keywords": ["combustível", "gasolina", "uber", "taxi"]
            },
            "Moradia": {
                "examples": ["TRANSF TAMIRES"],
                "keywords": ["aluguel", "condomínio", "energia", "água"]
            },
            "Saúde": {
                "keywords": ["farmácia", "hospital", "médico", "clínica"]
            },
            "Transferências para terceiros": {
                "examples": ["PIX TRANSF"],
                "keywords": ["pix", "transferência", "ted"]
            }
        }