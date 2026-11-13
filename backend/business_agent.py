
import re


# ==================================================
# 1. BUSINESS KEYWORD CATEGORIES
# ==================================================

BUSINESS_CATEGORIES = {

    "revenue": {
        "keywords": [
            "revenue",
            "income",
            "earnings",
            "revenue growth",
            "sales revenue",
            "recurring revenue",
            "monthly revenue",
            "annual revenue",
            "revenue decline",
            "revenue loss",
        ],
        "review_question": (
            "Is the business generating sufficient and sustainable revenue?"
        ),
        "recommended_check": (
            "Review revenue trends, income sources, recurring revenue, "
            "and revenue growth."
        ),
    },

    "profitability": {
        "keywords": [
            "profit",
            "profitability",
            "net profit",
            "gross profit",
            "operating profit",
            "profit margin",
            "loss",
            "losses",
            "operational costs",
            "operating costs",
            "increasing operational costs",
            "operational expenses",
            "operating expenses",
            "cost reduction",
            "cost optimization",
            "high expenses",
            "rising costs",
        ],
        "review_question": "Is the business operating profitably?",
        "recommended_check": (
            "Review profit margins, operating expenses, cost structure, "
            "operational costs, and overall financial performance."
        ),
    },

    "market_analysis": {
        "keywords": [
            "market",
            "market share",
            "market demand",
            "target market",
            "market trends",
            "competitor",
            "competition",
            "customer segment",
        ],
        "review_question": (
            "Is the business positioned effectively in its target market?"
        ),
        "recommended_check": (
            "Review market demand, competitor activity, customer segments, "
            "and market opportunities."
        ),
    },

    "business_growth": {
        "keywords": [
            "growth",
            "business expansion",
            "scaling",
            "expansion",
            "customer acquisition",
            "customer retention",
            "business development",
            "customer satisfaction",
            "customer drop-offs",
            "customer churn",
            "customer loyalty",
            "repeat purchases",
            "customer lifetime value",
            "abandon shopping carts",
            "abandoned shopping carts",
            "shopping cart abandonment",
            "cart abandonment",
            "abandoned carts",
            "customer complaints",
            "customer complaint",
            "customer loss",
            "losing customers",
            "loss of customers",
            "customer dissatisfaction",
            "customer feedback",
            "customer experience",
            "customer retention rate",
            "customer acquisition cost",
        ],
        "review_question": (
            "Does the business have opportunities for sustainable growth?"
        ),
        "recommended_check": (
            "Review growth trends, customer acquisition, retention, "
            "customer complaints, expansion opportunities, and business strategy."
        ),
    },

    "business_model": {
        "keywords": [
            "business model",
            "subscription model",
            "revenue model",
            "value proposition",
            "business strategy",
            "operating model",
        ],
        "review_question": (
            "Is the business model suitable and sustainable?"
        ),
        "recommended_check": (
            "Review the value proposition, revenue model, operating model, "
            "and long-term business sustainability."
        ),
    },

    "pricing": {
        "keywords": [
            "pricing",
            "price",
            "discount",
            "pricing strategy",
            "product cost",
            "service cost",
        ],
        "review_question": (
            "Is the pricing strategy appropriate for the market and customers?"
        ),
        "recommended_check": (
            "Review pricing structure, customer willingness to pay, "
            "competitor pricing, and discount policies."
        ),
    },

    "sales": {
        "keywords": [
            "sales",
            "sales growth",
            "sales performance",
            "sales conversion",
            "conversion rate",
            "sales pipeline",
            "declining sales",
            "sales decline",
            "low conversion",
        ],
        "review_question": (
            "Is the business converting potential customers into sales effectively?"
        ),
        "recommended_check": (
            "Review sales trends, conversion rates, sales pipeline, "
            "and customer purchasing behavior."
        ),
    },

    "investment": {
        "keywords": [
            "investment",
            "investor",
            "funding",
            "capital",
            "return on investment",
            "roi",
            "financial resources",
        ],
        "review_question": (
            "Are investments and financial resources being used effectively?"
        ),
        "recommended_check": (
            "Review investment allocation, funding requirements, "
            "expected returns, and financial risks."
        ),
    },
}


# ==================================================
# 2. BUSINESS PRIORITY MAPPING
# ==================================================

BUSINESS_PRIORITY = {

    "revenue": "high",

    "profitability": "high",

    "market_analysis": "low",

    "business_growth": "medium",

    "business_model": "medium",

    "pricing": "medium",

    "sales": "high",

    "investment": "medium",

}


# ==================================================
# 3. SENTENCE PROCESSING
# ==================================================

def split_sentences(content: str) -> list:
    """Split content into individual sentences."""

    return [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", content)
        if sentence.strip()
    ]


# ==================================================
# 4. BUSINESS ANALYSIS AGENT
# ==================================================

def business_analysis_agent(content: str) -> dict:
    """Identify business information and generate review suggestions."""

    findings = []

    for sentence in split_sentences(content):

        sentence_lower = sentence.lower()

        matched_categories = []
        matched_keywords = []

        # Identify matching business categories
        for category, details in BUSINESS_CATEGORIES.items():

            category_matches = [
                keyword
                for keyword in details["keywords"]
                if re.search(
                    r"(?<!\w)" + re.escape(keyword) + r"(?!\w)",
                    sentence_lower
                )
            ]

            if category_matches:

                matched_categories.append(category)

                matched_keywords.extend(category_matches)

        # Generate structured findings
        if matched_categories:

            primary_category = matched_categories[0]

            primary_details = BUSINESS_CATEGORIES[primary_category]

            # Determine preliminary finding priority
            priority = BUSINESS_PRIORITY.get(
                primary_category,
                "low"
            )

            findings.append({

                "observation": sentence,

                "business_area": matched_categories,

                "matched_keywords": matched_keywords,

                "priority": priority,

                "review_question": primary_details["review_question"],

                "recommended_check": (
                    primary_details["recommended_check"]
                ),

                "status": "requires_review",

            })

    return {

        "agent": "business_analysis",

        "total_findings": len(findings),

        "findings": findings,

        "note": (
            "The agent identifies business-related information and "
            "generates preliminary review suggestions. These findings "
            "are not verified business conclusions or financial assessments. "
            "Priority levels are preliminary category-based assessments."
        ),

    }
