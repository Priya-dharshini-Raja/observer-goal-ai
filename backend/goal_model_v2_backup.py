
import re
from sentence_transformers import SentenceTransformer, util


# ==================================================
# 1. KEYWORD DATABASE
# ==================================================

GOAL_KEYWORDS = {
    "security": [
        "security", "cybersecurity", "vulnerability",
        "vulnerabilities", "attack", "attacks",
        "authentication", "authorization", "password",
        "encryption", "access control", "privacy",
        "sql injection", "session hijacking",
        "session management", "cross-site scripting",
        "cross site scripting", "xss",
        "cross-site request forgery", "csrf",
        "multi-factor authentication", "firewall",
        "network security", "account recovery",
        "security logging", "sensitive data",
        "confidential information", "secure communication",
        "authentication tokens", "unauthorized access",
        "data protection", "brute force",
        "brute-force", "login attempts", "login protection",
        "insecure direct object reference", "idor",
        "session expiration", "session timeout",
        "sessions expire after inactivity",
        "session expires after inactivity",
        "session inactivity timeout",
        "inactive session timeout",
        "user permissions", "restricted resources",
        "malicious file uploads", "file upload security",
        "suspicious login", "password reset",
        "access restriction", "privilege escalation"
    ],

    "business": [
        "business", "revenue", "profit", "profitability",
        "market", "sales", "growth", "customer",
        "business model", "pricing", "investment",
        "financial", "financial sustainability",
        "subscription", "recurring revenue",
        "customer retention", "competitive position",
        "business expansion", "operating costs",
        "customer acquisition", "marketing strategy",
        "revenue diversification", "customer churn",
        "monetization", "customer lifetime value",
        "market opportunities", "financial performance",
        "commercial value", "commercial benefits",
        "return on investment", "roi",
        "new regions", "market entry",
        "competitive advantage", "financial risks",
        "long-term profitability", "income generation",
        "pricing strategy", "customer lifetime",
        "market share", "business sustainability"
    ],

    "technical": [
        "technical", "architecture", "api", "rest api",
        "database", "database design", "integration",
        "system performance", "performance", "backend",
        "infrastructure", "scalability",
        "software components", "modularity",
        "backend service", "horizontal scaling",
        "vertical scaling", "error handling",
        "caching", "cache", "load balancing",
        "external service integration", "data processing",
        "deployment architecture", "system bottlenecks",
        "codebase", "code maintainability",
        "resource utilization", "api endpoints",
        "database optimization", "query optimization",
        "system reliability", "software engineering",
        "application deployment", "concurrent requests",
        "memory management", "network timeouts",
        "message queue", "containerization",
        "api versioning", "file storage",
        "file retrieval", "fault tolerance",
        "service communication", "database queries",
        "server requests", "system architecture",
        "application services", "request handling",
        "storage efficiency", "service reliability"
    ],

    "user_experience": [
        "user experience", "usability", "navigation",
        "accessibility", "interface", "interface design",
        "visual design", "responsive", "layout",
        "readability", "user interface", "user interaction",
        "task completion", "interface elements",
        "labels and instructions", "keyboard accessibility",
        "keyboard navigation", "text readability",
        "navigation feedback", "interactive elements",
        "user onboarding", "error messages", "colors",
        "typography", "mobile screens", "mobile devices",
        "finding information", "important information",
        "user feedback", "interaction flow",
        "browsing experience", "visual appearance",
        "ease of use", "user satisfaction",
        "interface consistency", "website usability",
        "user tasks", "first-time visitors",
        "homepage clarity", "form guidance",
        "visually noticeable", "loading indicators",
        "undo actions", "page layouts",
        "checkout process", "clear icons",
        "help section", "confirmation messages",
        "registration process", "search experience",
        "finding relevant content", "visual prominence",
        "form fields", "user guidance"
    ]
}


# ==================================================
# 2. SEMANTIC GOAL DESCRIPTIONS
# ==================================================

GOAL_DESCRIPTIONS = {
    "security": (
        "Cybersecurity and application security analysis. "
        "Evaluate protection against brute force attacks, "
        "unauthorized access, insecure direct object references, "
        "malicious uploads, password attacks, session weaknesses, "
        "authentication failures, permission problems, data theft, "
        "privacy violations and security vulnerabilities."
    ),

    "business": (
        "Business and commercial analysis. Evaluate market potential, "
        "revenue generation, profitability, financial sustainability, "
        "customer acquisition, customer retention, subscriptions, "
        "pricing strategies, competitive advantages, market expansion, "
        "commercial value, investment returns and business risks."
    ),

    "technical": (
        "Software engineering and system implementation analysis. "
        "Evaluate concurrent server requests, memory management, "
        "network timeouts, message queues, containerization, API "
        "versioning, database queries, file storage, fault tolerance, "
        "system architecture, service communication, infrastructure, "
        "scalability, reliability and technical performance."
    ),

    "user_experience": (
        "User experience and usability evaluation. Examine whether "
        "visitors understand a homepage, forms provide helpful guidance, "
        "important actions are noticeable, loading indicators are clear, "
        "users can undo actions, layouts are consistent, checkout is "
        "straightforward, icons are understandable, help is easy to find, "
        "and confirmation messages and navigation support users."
    ),

    "general": (
        "General overview, neutral summary and broad description of "
        "provided information. Summarize the overall content, explain "
        "what the material is about, describe its major elements, provide "
        "a balanced account, present an objective overview, integrate "
        "different details and describe the supplied material without "
        "focusing on any single specialized area."
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

    if total <= 0:
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

            pattern = (
                r"(?<!\w)" + re.escape(keyword) + r"(?!\w)"
            )

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

    primary_goal = max(
        semantic_scores,
        key=semantic_scores.get
    )

    return {
        "primary_goal": primary_goal,
        "goal_weights": normalize_weights({
            primary_goal: semantic_scores[primary_goal]
        }),
        "method": "semantic",
        "semantic_scores": semantic_scores
    }


# ==================================================
# 7. HYBRID GOAL DETECTION
# ==================================================

def detect_goals_hybrid(user_query):

    keyword_result = detect_goals_keyword(user_query)

    semantic_result = detect_goals_semantic(user_query)

    goals = list(GOAL_DESCRIPTIONS.keys())

    keyword_scores = keyword_result["keyword_scores"]

    semantic_scores = semantic_result["semantic_scores"]

    total_keywords = sum(keyword_scores.values())

    # --------------------------------------------------
    # 7.1 EXPLICIT GENERAL INTENT
    # --------------------------------------------------

    general_patterns = [
        r"\bsummarize\b",
        r"\bsummary\b",
        r"\boverall\b",
        r"\bgeneral overview\b",
        r"\bneutral overview\b",
        r"\bobjective overview\b",
        r"\bbalanced overview\b",
        r"\bmajor elements\b",
        r"\bbroad descriptive level\b",
        r"\bintegrated overview\b",
        r"\bgeneral account\b",
        r"\bprovided content\b",
        r"\bsupplied information\b",
        r"\bwithout focusing on\b",
        r"\bcontent as a whole\b",
        r"\bwhat .* about overall\b"
    ]

    has_general_intent = any(
        re.search(pattern, user_query.lower())
        for pattern in general_patterns
    )

    # Explicit General intent takes priority only when
    # there are no specialized keyword matches.

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

    # --------------------------------------------------
    # 7.2 NORMALIZE KEYWORD SCORES
    # --------------------------------------------------

    if total_keywords > 0:

        keyword_weights = {
            goal: keyword_scores.get(goal, 0) / total_keywords
            for goal in goals
        }

    else:

        keyword_weights = {
            goal: 0.0 for goal in goals
        }

    # --------------------------------------------------
    # 7.3 SEMANTIC CONFIDENCE
    # --------------------------------------------------

    # Use the relative semantic ranking rather than
    # rejecting every score below a fixed threshold.

    specialized_goals = [
        "security",
        "business",
        "technical",
        "user_experience"
    ]

    highest_specialized = max(
        semantic_scores[goal]
        for goal in specialized_goals
    )

    highest_semantic = max(semantic_scores.values())

    semantic_confidence = {}

    for goal in goals:

        score = semantic_scores[goal]

        confidence = max(0.0, score)

        semantic_confidence[goal] = confidence

    # --------------------------------------------------
    # 7.4 CALCULATE HYBRID SCORES
    # --------------------------------------------------

    hybrid_scores = {}

    for goal in goals:

        if goal == "general":

            hybrid_scores[goal] = (
                0.20 * semantic_confidence[goal]
            )

        else:

            hybrid_scores[goal] = (
                0.40 * keyword_weights[goal]
                + 0.60 * semantic_confidence[goal]
            )

    # --------------------------------------------------
    # 7.5 SELECT PRIMARY GOAL
    # --------------------------------------------------

    if total_keywords > 0:

        # Explicit domain vocabulary is strong evidence.
        # Semantic evidence helps resolve competing goals.

        specialized_scores = {
            goal: hybrid_scores[goal]
            for goal in specialized_goals
        }

        primary_goal = max(
            specialized_scores,
            key=specialized_scores.get
        )

        # If no keyword category is present, compare
        # General and specialized semantic scores.

    else:

        primary_goal = max(
            semantic_scores,
            key=semantic_scores.get
        )

        # General is selected when its semantic score
        # is higher than every specialized category.

    # --------------------------------------------------
    # 7.6 SELECT RELEVANT GOALS
    # --------------------------------------------------

    selected_goals = {}

    if primary_goal == "general":

        selected_goals = {
            "general": hybrid_scores["general"]
        }

    else:

        for goal in specialized_goals:

            has_keyword = keyword_scores[goal] > 0

            has_semantic_support = (
                semantic_scores[goal]
                >= highest_specialized - 0.10
            )

            if has_keyword or has_semantic_support:

                selected_goals[goal] = hybrid_scores[goal]

    # --------------------------------------------------
    # 7.7 NORMALIZE FINAL WEIGHTS
    # --------------------------------------------------

    if not selected_goals or sum(selected_goals.values()) <= 0:

        selected_goals = {
            "general": 1.0
        }

        primary_goal = "general"

    weights = normalize_weights(selected_goals)

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
