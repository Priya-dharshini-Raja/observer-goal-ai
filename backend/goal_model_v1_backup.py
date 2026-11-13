
import re
from sentence_transformers import SentenceTransformer, util


# ==================================================
# 1. KEYWORD DATABASE
# ==================================================

GOAL_KEYWORDS = {
    "security": [
        "security",
        "cybersecurity",
        "vulnerability",
        "vulnerabilities",
        "attack",
        "attacks",
        "authentication",
        "authorization",
        "password",
        "encryption",
        "access control",
        "privacy",
        "security risks",
        "sql injection",
        "session hijacking",
        "session management",
        "cross-site scripting",
        "cross site scripting",
        "xss",
        "cross-site request forgery",
        "cross site request forgery",
        "csrf",
        "multi-factor authentication",
        "multifactor authentication",
        "firewall",
        "network security",
        "account recovery",
        "security logging",
        "sensitive data",
        "confidential information",
        "secure communication",
        "authentication tokens",
        "authorization policies",
        "unauthorized access",
        "data protection"
    ],

    "business": [
        "business",
        "revenue",
        "profit",
        "profitability",
        "market",
        "sales",
        "growth",
        "customer",
        "business model",
        "pricing",
        "investment",
        "financial",
        "financial sustainability",
        "subscription",
        "recurring revenue",
        "customer retention",
        "competitive position",
        "business expansion",
        "operating costs",
        "customer acquisition",
        "marketing strategy",
        "revenue diversification",
        "customer churn",
        "monetization",
        "customer lifetime value",
        "market opportunities",
        "financial performance"
    ],

    "technical": [
        "technical",
        "architecture",
        "technical architecture",
        "api",
        "rest api",
        "database",
        "database design",
        "integration",
        "system performance",
        "performance",
        "backend",
        "infrastructure",
        "scalability",
        "software components",
        "modularity",
        "backend service",
        "horizontal scaling",
        "vertical scaling",
        "error handling mechanisms",
        "error handling",
        "caching",
        "cache",
        "load balancing",
        "external service integration",
        "service integration",
        "data processing",
        "deployment architecture",
        "system bottlenecks",
        "codebase",
        "code maintainability",
        "resource utilization",
        "api endpoints",
        "database optimization",
        "query optimization",
        "system reliability",
        "software engineering",
        "system execution",
        "application deployment"
    ],

    "user_experience": [
        "user experience",
        "usability",
        "navigation",
        "accessibility",
        "interface",
        "interface design",
        "visual design",
        "responsive",
        "layout",
        "readability",
        "user interface",
        "user interaction",
        "task completion",
        "interface elements",
        "labels and instructions",
        "keyboard accessibility",
        "keyboard navigation",
        "text readability",
        "navigation feedback",
        "interactive elements",
        "user onboarding",
        "error messages",
        "understandable error messages",
        "colors",
        "typography",
        "mobile screens",
        "mobile devices",
        "finding information",
        "important information",
        "user feedback",
        "interaction flow",
        "browsing experience",
        "visual appearance",
        "ease of use",
        "user satisfaction",
        "interface consistency",
        "website usability",
        "user tasks"
    ]
}


# ==================================================
# 2. SEMANTIC GOAL DESCRIPTIONS
# ==================================================

GOAL_DESCRIPTIONS = {
    "security": (
        "Analyze cybersecurity and website security, including "
        "authentication, authorization, passwords, access control, "
        "encryption, data protection, privacy, vulnerabilities, "
        "SQL injection, session hijacking, cross-site scripting, "
        "cross-site request forgery, network security and threats."
    ),

    "business": (
        "Analyze business performance and financial health. "
        "Evaluate revenue, profitability, sales, customer acquisition, "
        "customer retention, subscription models, pricing, investment, "
        "marketing, operating costs, market opportunities, business "
        "growth and financial sustainability."
    ),

    "technical": (
        "Analyze software engineering and technical implementation, "
        "including software architecture, APIs, databases, backend "
        "services, infrastructure, system integration, caching, "
        "error handling, load balancing, deployment, scalability, "
        "performance, data processing and resource utilization."
    ),

    "user_experience": (
        "Analyze user experience and interface quality, including "
        "website usability, navigation, accessibility, keyboard "
        "interaction, visual design, readability, labels, instructions, "
        "interface consistency, error messages, user feedback, "
        "responsive design, mobile usability and task completion."
    )
}


# ==================================================
# 3. LOAD SEMANTIC MODEL
# ==================================================

_model = None
_goal_embeddings = None


def load_semantic_model():

    global _model, _goal_embeddings

    if _model is None:

        print("Loading semantic model...")

        _model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )

        descriptions = list(GOAL_DESCRIPTIONS.values())

        _goal_embeddings = _model.encode(
            descriptions,
            convert_to_tensor=True,
            normalize_embeddings=True
        )

        print("Semantic model loaded successfully.")

    return _model, _goal_embeddings


# ==================================================
# 4. HELPER FUNCTION
# ==================================================

def normalize_weights(scores):

    total = sum(scores.values())

    if total == 0:
        return {}

    weights = {
        goal: round(score / total, 2)
        for goal, score in scores.items()
        if score > 0
    }

    if weights:
        primary_goal = max(weights, key=weights.get)

        difference = round(1.0 - sum(weights.values()), 2)

        weights[primary_goal] = round(
            weights[primary_goal] + difference, 2
        )

    return weights


# ==================================================
# 5. KEYWORD-BASED GOAL DETECTION
# ==================================================

def detect_goals_keyword(user_query):

    query = user_query.lower()

    scores = {}

    for goal, keywords in GOAL_KEYWORDS.items():

        count = 0

        for keyword in keywords:

            pattern = r"(?<!\w)" + re.escape(keyword) + r"(?!\w)"

            if re.search(pattern, query):
                count += 1

        scores[goal] = count

    total = sum(scores.values())

    if total == 0:

        return {
            "primary_goal": "general",
            "goal_weights": {"general": 1.0},
            "method": "keyword",
            "keyword_scores": scores
        }

    weights = normalize_weights(scores)

    primary_goal = max(scores, key=scores.get)

    return {
        "primary_goal": primary_goal,
        "goal_weights": weights,
        "method": "keyword",
        "keyword_scores": scores
    }


# ==================================================
# 6. SEMANTIC-BASED GOAL DETECTION
# ==================================================

def detect_goals_semantic(user_query):

    model, goal_embeddings = load_semantic_model()

    query_embedding = model.encode(
        user_query,
        convert_to_tensor=True,
        normalize_embeddings=True
    )

    similarities = util.cos_sim(
        query_embedding,
        goal_embeddings
    )[0]

    goals = list(GOAL_DESCRIPTIONS.keys())

    semantic_scores = {
        goal: round(float(similarities[index]), 4)
        for index, goal in enumerate(goals)
    }

    highest_score = max(semantic_scores.values())

    if highest_score < 0.35:

        return {
            "primary_goal": "general",
            "goal_weights": {"general": 1.0},
            "method": "semantic",
            "semantic_scores": semantic_scores
        }

    selected_goals = {
        goal: score
        for goal, score in semantic_scores.items()
        if score >= max(0.35, highest_score - 0.08)
    }

    weights = normalize_weights(selected_goals)

    primary_goal = max(selected_goals, key=selected_goals.get)

    return {
        "primary_goal": primary_goal,
        "goal_weights": weights,
        "method": "semantic",
        "semantic_scores": semantic_scores
    }


# ==================================================
# 7. HYBRID GOAL DETECTION
# ==================================================

def detect_goals_hybrid(user_query):

    # Run keyword detection
    keyword_result = detect_goals_keyword(user_query)

    # Run semantic detection
    semantic_result = detect_goals_semantic(user_query)

    goals = list(GOAL_DESCRIPTIONS.keys())

    keyword_scores = keyword_result["keyword_scores"]

    semantic_scores = semantic_result["semantic_scores"]

    total_keywords = sum(keyword_scores.values())

    # ==================================================
    # 7.1 EXPLICIT GENERAL-INTENT DETECTION
    # ==================================================

    general_patterns = [

        r"\bgeneral overview\b",
        r"\boverall overview\b",
        r"\bgeneral analysis\b",
        r"\boverall analysis\b",
        r"\ball-round analysis\b",
        r"\bgive me an overview\b",
        r"\bcomplete overview\b",
        r"\boverall characteristics\b",
        r"\bdifferent aspects\b",
        r"\boverall assessment\b",
        r"\bsummarize the different aspects\b",
        r"\bwithout focusing on one area\b",
        r"\bwithout focusing on any one area\b",

        r"\bhigh-level summary\b",
        r"\bhigh level summary\b",
        r"\bcomprehensive review\b",
        r"\ball major areas\b",
        r"\bbroad assessment\b",
        r"\bcomplete picture\b",
        r"\bmultiple perspectives\b",
        r"\bbalanced evaluation\b",
        r"\bmain characteristics\b",
        r"\boverall summary\b",
        r"\bcontent as a whole\b",
        r"\bentire system\b",
        r"\bcomplete assessment\b",
        r"\bmajor observations\b",
        r"\bhigh-level evaluation\b",
        r"\bhigh level evaluation\b",
        r"\ball important aspects\b",
        r"\bbroad understanding\b",
        r"\boverall nature\b",
        r"\bwhole website\b",
        r"\bwhole system\b",
        r"\bentire website\b",
        r"\bwithout prioritizing\b",
        r"\bwithout prioritising\b"
    ]

    has_general_intent = any(
        re.search(pattern, user_query.lower())
        for pattern in general_patterns
    )

    # General intent is selected only when no specialized
    # keyword is explicitly present.

    if has_general_intent and total_keywords == 0:

        return {
            "primary_goal": "general",
            "goal_weights": {"general": 1.0},
            "method": "hybrid",
            "keyword_scores": keyword_scores,
            "semantic_scores": semantic_scores,
            "hybrid_scores": {
                goal: 0.0 for goal in goals
            }
        }

    # ==================================================
    # 7.2 NORMALIZE KEYWORD SCORES
    # ==================================================

    if total_keywords > 0:

        keyword_weights = {
            goal: keyword_scores[goal] / total_keywords
            for goal in goals
        }

    else:

        keyword_weights = {
            goal: 0.0 for goal in goals
        }

    # ==================================================
    # 7.3 SEMANTIC CONFIDENCE
    # ==================================================

    semantic_confidence = {}

    for goal in goals:

        score = semantic_scores[goal]

        confidence = (score - 0.25) / (0.65 - 0.25)

        confidence = max(0.0, min(1.0, confidence))

        semantic_confidence[goal] = confidence

    highest_semantic = max(semantic_scores.values())

    # ==================================================
    # 7.4 GENERAL QUERY FALLBACK
    # ==================================================

    if total_keywords == 0 and highest_semantic < 0.35:

        return {
            "primary_goal": "general",
            "goal_weights": {"general": 1.0},
            "method": "hybrid",
            "keyword_scores": keyword_scores,
            "semantic_scores": semantic_scores,
            "semantic_confidence": {
                goal: round(score, 4)
                for goal, score in semantic_confidence.items()
            },
            "hybrid_scores": {
                goal: 0.0 for goal in goals
            }
        }

    # ==================================================
    # 7.5 CALCULATE HYBRID SCORES
    # ==================================================

    # Experimental weights:
    # 30% keyword evidence
    # 70% semantic evidence

    hybrid_scores = {}

    for goal in goals:

        hybrid_scores[goal] = (
            0.30 * keyword_weights[goal]
            +
            0.70 * semantic_confidence[goal]
        )

    # ==================================================
    # 7.6 SELECT MEANINGFUL GOALS
    # ==================================================

    selected_goals = {}

    for goal in goals:

        has_keyword_match = keyword_scores[goal] > 0

        has_semantic_match = (
            semantic_scores[goal] >= 0.35
            and semantic_scores[goal] >= highest_semantic - 0.08
        )

        if has_keyword_match or has_semantic_match:

            selected_goals[goal] = hybrid_scores[goal]

    # ==================================================
    # 7.7 GENERAL FALLBACK
    # ==================================================

    if not selected_goals:

        return {
            "primary_goal": "general",
            "goal_weights": {"general": 1.0},
            "method": "hybrid",
            "keyword_scores": keyword_scores,
            "semantic_scores": semantic_scores,
            "semantic_confidence": {
                goal: round(score, 4)
                for goal, score in semantic_confidence.items()
            },
            "hybrid_scores": {
                goal: round(score, 4)
                for goal, score in hybrid_scores.items()
            }
        }

    # ==================================================
    # 7.8 NORMALIZE HYBRID SCORES
    # ==================================================

    total_hybrid = sum(selected_goals.values())

    if total_hybrid <= 0:

        return {
            "primary_goal": "general",
            "goal_weights": {"general": 1.0},
            "method": "hybrid",
            "keyword_scores": keyword_scores,
            "semantic_scores": semantic_scores,
            "hybrid_scores": hybrid_scores
        }

    weights = normalize_weights(selected_goals)

    primary_goal = max(selected_goals, key=selected_goals.get)

    # ==================================================
    # 7.9 RETURN HYBRID RESULT
    # ==================================================

    return {
        "primary_goal": primary_goal,
        "goal_weights": weights,
        "method": "hybrid",
        "keyword_scores": keyword_scores,
        "semantic_scores": semantic_scores,
        "semantic_confidence": {
            goal: round(score, 4)
            for goal, score in semantic_confidence.items()
        },
        "hybrid_scores": {
            goal: round(score, 4)
            for goal, score in hybrid_scores.items()
        }
    }


# ==================================================
# 8. MAIN FUNCTION
# ==================================================

def detect_goals(user_query):

    return detect_goals_hybrid(user_query)
