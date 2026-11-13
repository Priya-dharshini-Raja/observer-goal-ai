
import re


UX_CATEGORIES = {
    "usability": {
        "keywords": [
            "usability",
            "user friendly",
            "ease of use",
            "user interaction",
            "user satisfaction",
            "user journey",
            "user friction",
            "difficult to use",
            "complicated process",
            "too many steps",
            "task completion",
            "user drop-offs",
            "customer drop-offs",
            "customer satisfaction",
            "abandon their shopping carts",
            "abandon shopping carts",
            "abandoned shopping carts",
            "shopping cart abandonment",
            "cart abandonment",
            "checkout abandonment",
            "difficult checkout",
            "complicated checkout",
            "checkout process",
            "registration process",
            "complicated registration",
        ],
        "review_question": (
            "Can users complete their tasks easily and efficiently?"
        ),
        "recommended_check": (
            "Review task completion, interaction complexity, "
            "user feedback, checkout flow, and usability testing results."
        ),
    },

    "accessibility": {
        "keywords": [
            "accessibility",
            "screen reader",
            "keyboard navigation",
            "alt text",
            "color contrast",
            "wcag",
            "assistive technology",
        ],
        "review_question": (
            "Can users with different abilities access and use the application?"
        ),
        "recommended_check": (
            "Review keyboard accessibility, screen-reader compatibility, "
            "alternative text, color contrast, and accessibility standards."
        ),
    },

    "navigation": {
        "keywords": [
            "navigation",
            "menu",
            "navigation bar",
            "search functionality",
            "site structure",
            "page hierarchy",
        ],
        "review_question": (
            "Can users easily find the information they need?"
        ),
        "recommended_check": (
            "Review navigation menus, page hierarchy, search functionality, "
            "and movement between pages."
        ),
    },

    "interface_design": {
        "keywords": [
            "interface design",
            "user interface",
            "visual design",
            "interface",
            "design consistency",
            "ui design",
            "visual elements",
        ],
        "review_question": (
            "Is the interface visually consistent and easy to understand?"
        ),
        "recommended_check": (
            "Review visual hierarchy, typography, colors, component consistency, "
            "and interface organization."
        ),
    },

    "responsiveness": {
        "keywords": [
            "responsive",
            "responsive design",
            "mobile friendly",
            "mobile responsiveness",
            "screen size",
            "mobile layout",
            "cross-device",
        ],
        "review_question": (
            "Does the application work effectively across different devices "
            "and screen sizes?"
        ),
        "recommended_check": (
            "Review mobile, tablet, and desktop layouts, "
            "screen adaptation, and cross-device behavior."
        ),
    },

    "readability": {
        "keywords": [
            "readability",
            "font size",
            "typography",
            "text clarity",
            "content clarity",
            "line spacing",
            "content structure",
        ],
        "review_question": (
            "Can users read and understand the presented information easily?"
        ),
        "recommended_check": (
            "Review font sizes, text contrast, line spacing, "
            "content organization, and information clarity."
        ),
    },

    "feedback_and_loading": {
        "keywords": [
            "loading time",
            "loading experience",
            "loading indicator",
            "loading progress",
            "progress indicator",
            "error message",
            "error messages",
            "unclear error messages",
            "system feedback",
            "response feedback",
            "waiting time",
            "long loading times",
            "slow loading",
        ],
        "review_question": (
            "Does the application provide clear feedback and loading information?"
        ),
        "recommended_check": (
            "Review loading indicators, error messages, response feedback, "
            "and user communication during processing."
        ),
    },
}


# Preliminary UX priority levels based on category.
# These are review defaults, not verified severity measurements.
UX_PRIORITY = {
    "usability": "high",
    "accessibility": "high",
    "navigation": "medium",
    "interface_design": "low",
    "responsiveness": "medium",
    "readability": "medium",
    "feedback_and_loading": "high",
}


def split_sentences(content: str) -> list:
    """Split content into individual sentences."""

    return [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", content)
        if sentence.strip()
    ]


def ux_analysis_agent(content: str) -> dict:
    """Identify UX-related information and generate review suggestions."""

    findings = []

    for sentence in split_sentences(content):

        sentence_lower = sentence.lower()

        matched_categories = []
        matched_keywords = []

        for category, details in UX_CATEGORIES.items():

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

        if matched_categories:

            # Select the first matched category as the primary category.
            primary_category = matched_categories[0]

            primary_details = UX_CATEGORIES[primary_category]

            priority = UX_PRIORITY.get(primary_category, "medium")

            findings.append({
                "observation": sentence,
                "ux_area": matched_categories,
                "matched_keywords": matched_keywords,
                "priority": priority,
                "review_question": primary_details["review_question"],
                "recommended_check": primary_details["recommended_check"],
                "status": "requires_review",
            })

    return {
        "agent": "ux_analysis",
        "total_findings": len(findings),
        "findings": findings,
        "note": (
            "The agent identifies user-experience-related information and "
            "generates preliminary review suggestions. These findings "
            "are not verified UX problems or usability test results. "
            "Priority levels are preliminary category-based review defaults."
        ),
    }
