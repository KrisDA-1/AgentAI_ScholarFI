# services/discounts_service.py
import logging
import streamlit as st
from utils.scraper import get_products_by_categories, get_best_store_info
from utils.openai import analyze_products_with_llm
import random

logging.basicConfig(level=logging.INFO)

@st.cache_data(ttl=3600)
def get_top_discounts_simple(products: list, num_to_select: int = 5) -> list:
    if not products:
        return []
    selected = random.sample(products, min(num_to_select, len(products)))
    ai_templates = [
        "According to your recent spending patterns, you might benefit from reducing your expenses in the <span style='font-weight: bold;'>{category}</span> category. I found an offer at <span style='font-weight: bold;'>{store}</span>: the product '<span style='font-weight: bold;'>{title}</span>' is available for <span style='font-weight: bold;'>£{price}</span>. You can check it here: <a href='{link}' target='_blank' style='color: blue; text-decoration: underline;'>{link}</a>.",
        "Based on how you've been spending lately, you seem to be investing quite a bit in <span style='font-weight: bold;'>{category}</span>. A good deal I found for you is at <span style='font-weight: bold;'>{store}</span>: '<span style='font-weight: bold;'>{title}</span>' for only <span style='font-weight: bold;'>£{price}</span>. Here is the direct link: <a href='{link}' target='_blank' style='color: blue; text-decoration: underline;'>{link}</a>.",
        "Your recent purchases suggest you frequently buy items related to <span style='font-weight: bold;'>{category}</span>. To help you save, I located an offer at <span style='font-weight: bold;'>{store}</span>: '<span style='font-weight: bold;'>{title}</span>' priced at <span style='font-weight: bold;'>£{price}</span>. You can access it here: <a href='{link}' target='_blank' style='color: blue; text-decoration: underline;'>{link}</a>.",
        "Analyzing your expenditure trends, I've noticed a focus on <span style='font-weight: bold;'>{category}</span>. To optimize your budget, consider this deal from <span style='font-weight: bold;'>{store}</span>: '<span style='font-weight: bold;'>{title}</span>' at just <span style='font-weight: bold;'>£{price}</span>. Visit the link: <a href='{link}' target='_blank' style='color: blue; text-decoration: underline;'>{link}</a>.",
        "From your transaction history, it appears you're spending significantly on <span style='font-weight: bold;'>{category}</span>. Here's a savings opportunity at <span style='font-weight: bold;'>{store}</span>: '<span style='font-weight: bold;'>{title}</span>' for <span style='font-weight: bold;'>£{price}</span>. Check it out here: <a href='{link}' target='_blank' style='color: blue; text-decoration: underline;'>{link}</a>.",
        "Based on your financial habits, reducing costs in <span style='font-weight: bold;'>{category}</span> could be beneficial. I recommend this offer from <span style='font-weight: bold;'>{store}</span>: '<span style='font-weight: bold;'>{title}</span>' priced at <span style='font-weight: bold;'>£{price}</span>. Direct link: <a href='{link}' target='_blank' style='color: blue; text-decoration: underline;'>{link}</a>.",
        "Your spending data indicates a preference for <span style='font-weight: bold;'>{category}</span> items. To help you save, I've found a great deal at <span style='font-weight: bold;'>{store}</span>: '<span style='font-weight: bold;'>{title}</span>' for only <span style='font-weight: bold;'>£{price}</span>. Access it here: <a href='{link}' target='_blank' style='color: blue; text-decoration: underline;'>{link}</a>.",
        "Considering your recent purchases in <span style='font-weight: bold;'>{category}</span>, this promotion at <span style='font-weight: bold;'>{store}</span> caught my attention: '<span style='font-weight: bold;'>{title}</span>' at <span style='font-weight: bold;'>£{price}</span>. Here's the link to explore: <a href='{link}' target='_blank' style='color: blue; text-decoration: underline;'>{link}</a>.",
        "To align with your budgeting goals, I suggest checking out this deal in <span style='font-weight: bold;'>{category}</span> from <span style='font-weight: bold;'>{store}</span>: '<span style='font-weight: bold;'>{title}</span>' for <span style='font-weight: bold;'>£{price}</span>. Visit the store directly: <a href='{link}' target='_blank' style='color: blue; text-decoration: underline;'>{link}</a>.",
        "Your expense patterns show interest in <span style='font-weight: bold;'>{category}</span>. For potential savings, look at this offer at <span style='font-weight: bold;'>{store}</span>: '<span style='font-weight: bold;'>{title}</span>' priced at <span style='font-weight: bold;'>£{price}</span>. Link to purchase: <a href='{link}' target='_blank' style='color: blue; text-decoration: underline;'>{link}</a>.",
    ]
    template_indices = random.sample(range(len(ai_templates)), min(5, len(ai_templates)))
    messages = []
    for i, p in enumerate(selected[:4]):
        template_index = template_indices[i] if i < len(template_indices) else random.randint(0, len(ai_templates) - 1)
        template = ai_templates[template_index]
        msg = template.format(
            category=p.get("category", "this category"),
            store=p.get("store", "Unknown Store"),
            title=p.get("title", "Unknown Product"),
            price=p.get("best_price", "?"),
            link=p.get("store_link", "#")
        )
        messages.append({"text": msg})
    
    return messages[:3]

@st.cache_data(ttl=3600)
def get_top_discounts(queries: list[str], user_context: dict = None) -> list:
    """
    Scrapea categorías → obtiene mejores precios → manda a IA → fallback si falla.
    """
    # 1) Products scraping
    scraped = get_products_by_categories(queries)
    if not scraped:
        logging.warning("No products scraped.")
        return []
    # 2) Add info and best prices
    detailed = get_best_store_info(scraped)
    # Filter only those with store and price
    detailed_products = [p for p in detailed if p.get("store") and p.get("best_price")]
    if not detailed_products:
        return get_top_discounts_simple([], 5)
    # 3) Payload for IA
    payload = {
        "user_summary": user_context or {},
        "products": detailed_products
    }

    try:
        result = analyze_products_with_llm(payload)

        if result and isinstance(result, dict) and result.get("selected"):
            formatted = []
            for item in result["selected"][:5]:
                text = (
                    f"<a href='{item.get('store_link', '#')}' target='_blank' ""style='color: blue; text-decoration: underline;'>"
                    f"<span style='font-weight: bold;'>{item.get('title')}</span> — "
                    f"<span style='font-weight: bold;'>£{item.get('best_price')}</span> "
                    f"({item.get('justification', '')})"
                    "</a>"
                )
                formatted.append({"text": text})  # Excel a 'text'
            # Fill if less than 3
            while len(formatted) < 3:
                extra = get_top_discounts_simple(detailed_products, 1)
                if not extra:
                    break
                formatted.extend(extra)

            return formatted[:3]
        # IA failed, fallback
        return get_top_discounts_simple(detailed_products, 3)
    
    except Exception as e:
        logging.error(f"IA error: {str(e)}")
        return get_top_discounts_simple(detailed_products, 3)
