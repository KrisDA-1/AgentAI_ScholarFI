# services/savings_recomender.py
import random
from datetime import datetime
from decimal import Decimal

def generate_savings_recommendations(transactions, goals):
    """
    Generate AI-styled personalized savings recommendations with varied structure.
    """
    if not goals:
        return [{"text": "Add a savings goal to receive personalized tips."}]
    
    if not transactions:
        return [{"text": "No transactions recorded yet."}]
    
    # Pick up to 2 random goals to mention per tip
    goal_names_all = [g.get("name", "your goal") for g in goals]
    
    # Aggregate expenses by category
    category_totals = {}
    for t in transactions:
        if t.get("type") != "expense":
            continue
        cat = t.get("category", "Other")
        category_totals[cat] = category_totals.get(cat, 0) + t.get("amount", 0)
    
    if not category_totals:
        return [{"text": "No expenses to analyze for this month."}]
    
    # Sort categories by total spent
    sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
    
    messages = []
    for i, (category, amount) in enumerate(sorted_categories[:3]):  # Top 3 categories
        factor = Decimal('0.05') + Decimal(str(random.random() * 0.1))
        suggested_saving = (amount * factor).quantize(Decimal('0.01'))
        days_remaining = max(1, 30 - datetime.now().day)
        daily_saving = round(suggested_saving / days_remaining, 2)
        months_saved = round(suggested_saving / 50, 1)  # example: £50/month goal
        
        # Pick 1 or 2 random goals for this tip
        goal_names = ", ".join(random.sample(goal_names_all, min(1, len(goal_names_all))))
        
        ai_templates = [
            f"To reach <span style='font-weight: bold;'>{goal_names}</span> faster, consider trimming <span style='font-weight: bold;'>{category}</span> expenses by <span style='font-weight: bold;'>£{suggested_saving}</span>. This small daily adjustment of <span style='font-weight: bold;'>£{daily_saving}</span> could save you approximately <span style='font-weight: bold;'>{months_saved}</span> months on your goal.",
            f"Your recent spending shows high investment in <span style='font-weight: bold;'>{category}</span>. Saving <span style='font-weight: bold;'>£{suggested_saving}</span> here could help you achieve <span style='font-weight: bold;'>{goal_names}</span> sooner. Even <span style='font-weight: bold;'>£{daily_saving}</span> per day adds up!",
            f"<span style='font-weight: bold;'>{goal_names}</span> could be reached quicker by reducing spending in <span style='font-weight: bold;'>{category}</span> by <span style='font-weight: bold;'>£{suggested_saving}</span>. This is roughly <span style='font-weight: bold;'>£{daily_saving}</span> per day and may shorten your timeline by <span style='font-weight: bold;'>{months_saved}</span> months.",
            f"Analyzing your transactions, focusing on <span style='font-weight: bold;'>{goal_names}</span> while saving <span style='font-weight: bold;'>£{suggested_saving}</span> from <span style='font-weight: bold;'>{category}</span> can significantly accelerate your savings. Daily adjustments of <span style='font-weight: bold;'>£{daily_saving}</span> make a big impact over time.",
            f"Consider allocating <span style='font-weight: bold;'>£{suggested_saving}</span> from <span style='font-weight: bold;'>{category}</span> to <span style='font-weight: bold;'>{goal_names}</span>. A small daily saving of <span style='font-weight: bold;'>£{daily_saving}</span> could help shorten your path by <span style='font-weight: bold;'>{months_saved}</span> months.",
            f"By slightly reducing <span style='font-weight: bold;'>{category}</span> expenses, you can progress faster towards <span style='font-weight: bold;'>{goal_names}</span>. Saving only <span style='font-weight: bold;'>£{daily_saving}</span> per day could reduce your goal timeline by <span style='font-weight: bold;'>{months_saved}</span> months.",
            f"Your spending trends suggest <span style='font-weight: bold;'>{category}</span> is a key area for optimization. Redirecting <span style='font-weight: bold;'>£{suggested_saving}</span> to <span style='font-weight: bold;'>{goal_names}</span> can significantly accelerate your financial progress.",
            f"To improve your savings trajectory, try saving <span style='font-weight: bold;'>£{suggested_saving}</span> from <span style='font-weight: bold;'>{category}</span>. This small daily change of <span style='font-weight: bold;'>£{daily_saving}</span> could bring you closer to <span style='font-weight: bold;'>{goal_names}</span> more quickly.",
            f"Focusing on <span style='font-weight: bold;'>{goal_names}</span>, reducing <span style='font-weight: bold;'>{category}</span> expenses by <span style='font-weight: bold;'>£{suggested_saving}</span> can shorten the time to achieve your goals by <span style='font-weight: bold;'>{months_saved}</span> months. Small consistent savings matter!",
            f"Consider making minor adjustments in <span style='font-weight: bold;'>{category}</span>. Saving <span style='font-weight: bold;'>£{suggested_saving}</span> here can impact your progress on <span style='font-weight: bold;'>{goal_names}</span> dramatically. Daily reductions of <span style='font-weight: bold;'>£{daily_saving}</span> add up over the month."
        ]
        
        template = random.choice(ai_templates)
        messages.append({"text": template})
    
    return messages[:3]  # return top 3 tips
