
import re


# ==================================================
# 1. TECHNICAL KEYWORD CATEGORIES
# ==================================================

TECHNICAL_CATEGORIES = {

    "architecture": {
        "keywords": [
            "architecture",
            "system design",
            "microservices",
            "monolithic",
            "backend",
            "frontend"
        ],
        "review_question": (
            "Is the system architecture appropriate for "
            "the application's requirements?"
        ),
        "recommended_check": (
            "Review component responsibilities, dependencies, "
            "and architectural design."
        )
    },

    "api": {
        "keywords": [
            "api",
            "rest api",
            "endpoint",
            "http",
            "api request",
            "api response"
        ],
        "review_question": (
            "Are the APIs designed and implemented appropriately?"
        ),
        "recommended_check": (
            "Review API documentation, input validation, "
            "error handling, and response consistency."
        )
    },

    "database": {
        "keywords": [
            "database",
            "sql",
            "mongodb",
            "mysql",
            "postgresql",
            "query",
            "data storage"
        ],
        "review_question": (
            "Is the database design suitable for the application?"
        ),
        "recommended_check": (
            "Review database schema, indexing, query efficiency, "
            "and data consistency."
        )
    },

    "integration": {
        "keywords": [
            "integration",
            "third-party",
            "external service",
            "payment gateway",
            "api integration"
        ],
        "review_question": (
            "Are the integrated services communicating reliably?"
        ),
        "recommended_check": (
            "Review service communication, error handling, "
            "and integration dependencies."
        )
    },

    "infrastructure": {
        "keywords": [
            "server",
            "cloud",
            "hosting",
            "infrastructure",
            "deployment"
        ],
        "review_question": (
            "Is the infrastructure configured appropriately?"
        ),
        "recommended_check": (
            "Review server configuration, deployment setup, "
            "resource usage, and availability."
        )
    },

    "scalability": {
        "keywords": [
            "scalability",
            "scalable",
            "load balancing",
            "concurrent users",
            "high traffic"
        ],
        "review_question": (
            "Can the system handle increasing workloads?"
        ),
        "recommended_check": (
            "Review load-testing results, resource limits, "
            "and scaling strategies."
        )
    },

    "performance": {
        "keywords": [
            "performance",
            "response time",
            "latency",
            "optimization",
            "slow",
            "throughput"
        ],
        "review_question": (
            "Does the application meet its performance requirements?"
        ),
        "recommended_check": (
            "Measure response times, resource consumption, "
            "and application bottlenecks."
        )
    },

    "technology": {
        "keywords": [
            "technology",
            "framework",
            "programming language",
            "software"
        ],
        "review_question": (
            "Are the selected technologies suitable for the project?"
        ),
        "recommended_check": (
            "Review technology compatibility, maintainability, "
            "and project requirements."
        )
    }
}


# ==================================================
# 2. TECHNICAL PRIORITY MAPPING
# ==================================================

TECHNICAL_PRIORITY = {

    "architecture": "low",

    "api": "medium",

    "database": "medium",

    "integration": "medium",

    "infrastructure": "high",

    "scalability": "high",

    "performance": "medium",

    "technology": "low"

}


# ==================================================
# 3. SENTENCE PROCESSING
# ==================================================

def split_sentences(content: str) -> list:

    sentences = re.split(r'(?<=[.!?])\s+', content)

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


# ==================================================
# 4. TECHNICAL ANALYSIS AGENT
# ==================================================

def technical_analysis_agent(content: str) -> dict:

    findings = []

    sentences = split_sentences(content)

    for sentence in sentences:

        sentence_lower = sentence.lower()

        matched_categories = []

        matched_keywords = []

        # Identify matching technical categories
        for category, details in TECHNICAL_CATEGORIES.items():

            category_matches = [
                keyword
                for keyword in details["keywords"]
                if re.search(
                    r"\b" + re.escape(keyword) + r"\b",
                    sentence_lower
                )
            ]

            if category_matches:

                matched_categories.append(category)

                matched_keywords.extend(category_matches)

        # Generate structured findings
        if matched_categories:

            primary_category = matched_categories[0]

            category_details = TECHNICAL_CATEGORIES[
                primary_category
            ]

            # Determine finding priority
            priority = TECHNICAL_PRIORITY.get(
                primary_category,
                "low"
            )

            findings.append({

                "observation": sentence,

                "technical_area": matched_categories,

                "matched_keywords": matched_keywords,

                "priority": priority,

                "review_question": (
                    category_details["review_question"]
                ),

                "recommended_check": (
                    category_details["recommended_check"]
                ),

                "status": "requires_review"

            })

    # Return analysis
    return {

        "agent": "technical_analysis",

        "total_findings": len(findings),

        "findings": findings,

        "note": (
            "The agent identifies technical information and "
            "generates preliminary review suggestions. "
            "These findings are not verified technical defects "
            "or confirmed performance issues. Priority levels "
            "are preliminary category-based assessments."
        )
    }
