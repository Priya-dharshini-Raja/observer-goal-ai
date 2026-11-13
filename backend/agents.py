
import re


# ==================================================
# 1. SECURITY KEYWORD CATEGORIES
# ==================================================

SECURITY_CATEGORIES = {

    "authentication": {
        "keywords": [
            "authentication",
            "login",
            "log in",
            "sign in",
            "multi-factor authentication",
            "two-factor authentication",
            "mfa",
            "otp",
        ],
        "review_question": "Are users' identities verified securely?",
        "recommended_check": (
            "Review login mechanisms, password policies, "
            "multi-factor authentication, and session management."
        ),
    },

    "authorization": {
        "keywords": [
            "authorization",
            "permission",
            "role-based access",
            "privilege",
            "access control",
            "unauthorized access",
        ],
        "review_question": (
            "Are users restricted to the resources they are allowed to access?"
        ),
        "recommended_check": (
            "Review user roles, permissions, access restrictions, "
            "and privilege escalation protections."
        ),
    },

    "data_protection": {
        "keywords": [
            "encryption",
            "encrypted",
            "data protection",
            "data security",
            "sensitive data",
            "personal information",
            "data breach",
        ],
        "review_question": (
            "Is sensitive information adequately protected?"
        ),
        "recommended_check": (
            "Review encryption at rest and in transit, "
            "data storage practices, and sensitive-data handling."
        ),
    },

    "password_security": {
        "keywords": [
            "password",
            "password hashing",
            "weak password",
            "password policy",
            "password storage",
        ],
        "review_question": (
            "Are passwords stored and managed securely?"
        ),
        "recommended_check": (
            "Review password hashing, password policies, "
            "reset mechanisms, and protection against brute-force attacks."
        ),
    },

    "vulnerability": {
        "keywords": [
            "vulnerability",
            "vulnerabilities",
            "security flaw",
            "security weakness",
            "sql injection",
            "cross-site scripting",
            "xss",
            "csrf",
        ],
        "review_question": (
            "Does the application contain potential security weaknesses?"
        ),
        "recommended_check": (
            "Perform security testing, dependency checks, "
            "input validation reviews, and vulnerability assessments."
        ),
    },

    "privacy": {
        "keywords": [
            "privacy",
            "user data",
            "personal data",
            "data collection",
            "data sharing",
            "privacy policy",
        ],
        "review_question": (
            "Is user information collected and handled appropriately?"
        ),
        "recommended_check": (
            "Review data collection, consent, retention, "
            "sharing practices, and privacy controls."
        ),
    },

    "network_security": {
        "keywords": [
            "firewall",
            "network security",
            "https",
            "ssl",
            "tls",
            "secure connection",
            "network traffic",
        ],
        "review_question": (
            "Are network communications adequately protected?"
        ),
        "recommended_check": (
            "Review network configuration, secure protocols, "
            "firewall rules, and communication security."
        ),
    },
}


# ==================================================
# 2. SECURITY PRIORITY MAPPING
# ==================================================

SECURITY_PRIORITY = {

    "authentication": "high",

    "authorization": "high",

    "data_protection": "high",

    "password_security": "high",

    "vulnerability": "high",

    "privacy": "medium",

    "network_security": "medium",

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
# 4. SECURITY ANALYSIS AGENT
# ==================================================

def security_analysis_agent(content: str) -> dict:
    """Identify security information and generate review suggestions."""

    findings = []

    for sentence in split_sentences(content):

        sentence_lower = sentence.lower()

        matched_categories = []

        matched_keywords = []

        # Identify matching security categories
        for category, details in SECURITY_CATEGORIES.items():

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

            primary_details = SECURITY_CATEGORIES[
                primary_category
            ]

            # Determine preliminary finding priority
            priority = SECURITY_PRIORITY.get(
                primary_category,
                "medium"
            )

            findings.append({

                "observation": sentence,

                "security_area": matched_categories,

                "matched_keywords": matched_keywords,

                "priority": priority,

                "review_question": (
                    primary_details["review_question"]
                ),

                "recommended_check": (
                    primary_details["recommended_check"]
                ),

                "status": "requires_review",

            })

    return {

        "agent": "security_analysis",

        "total_findings": len(findings),

        "findings": findings,

        "note": (
            "The agent identifies security-related information and "
            "generates preliminary review suggestions. These findings "
            "are not verified security vulnerabilities. Priority levels "
            "are preliminary category-based assessments and require "
            "security review."
        ),

    }
