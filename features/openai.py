# utils/openai.py
import json
import logging
import re
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv

# Upload .env variables
load_dotenv()

# Configuration logging
logging.basicConfig(level=logging.INFO)

# --- Initialize model (gpt-4o-mini) ---
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.2,
    max_tokens=800,
    openai_api_key=os.getenv("OPENAI_API_KEY")  # upload .env with your key
)

# --- Smart prompt ---
PROMPT = PromptTemplate.from_template("""
You are an AI expert in consumer savings.  
You will analyze user spending behavior and scraped supermarket products to select the BEST value deals.

USER SPENDING SUMMARY:
{spending_summary}

PRODUCT LIST (JSON):
{products_json}

TASK:
1. Identify the top 3 BEST DEALS based on:
   - Categories where user expenses INCREASED this month.
   - Price vs alternatives.
   - Unit price (if present).
   - General consumer savings value.

2. Output ONLY valid JSON using the structure:

{{
  "selected": [
    {{
      "store": "...",
      "title": "...",
      "best_price": "...",
      "store_link": "...",
      "justification": "..."
    }},
    {{
      "store": "...",
      "title": "...",
      "best_price": "...",
      "store_link": "...",
      "justification": "..."
    }},
    {{
      "store": "...",
      "title": "...",
      "best_price": "...",
      "store_link": "...",
      "justification": "..."
    }}
  ],
  "analysis": "...",
  "confidence": 0.0
}}

If you cannot identify 3 deals, return as many as possible (minimum 1 if available). If none, return empty selected.
""")

def analyze_products_with_llm(payload: dict) -> dict:
    """
    Envía productos + contexto al modelo gpt-4o-mini y retorna JSON parseado.
    Mantiene los nombres best_price y store_link para compatibilidad con Streamlit.
    """
    spending_summary = json.dumps(payload.get("user_summary", {}), indent=2)
    products_json = json.dumps(payload.get("products", []), indent=2)
    
    try:
        chain_input = {
            "spending_summary": spending_summary,
            "products_json": products_json
        }
        
        response = llm.invoke(PROMPT.format(**chain_input)).content
        
        # Extraer solo JSON
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            data = json.loads(json_str)
            return data
        else:
            logging.error("No JSON found in AI response.")
            return None
    
    except json.JSONDecodeError:
        logging.error("No se pudo parsear JSON del modelo. Respuesta:")
        logging.error(response)
        return None
    except Exception as e:
        logging.exception(f"Error ejecutando la IA: {str(e)}")
        return None
