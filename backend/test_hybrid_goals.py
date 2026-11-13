from goal_model import detect_goals_hybrid

test_queries = [
    "Find ways this website could lose money and improve its earnings",

    "Check whether hackers can gain unauthorized access to this platform",

    "Find problems in the software architecture and backend infrastructure",

    "Determine whether visitors can easily navigate and understand this website",

    "Give me a general overview of this content"
]

for query in test_queries:

    print("\n" + "=" * 70)
    print("QUERY:", query)

    result = detect_goals_hybrid(query)

    print("PRIMARY GOAL:", result["primary_goal"])
    print("GOAL WEIGHTS:", result["goal_weights"])
    print("METHOD:", result["method"])
    print("KEYWORD SCORES:", result["keyword_scores"])
    print("SEMANTIC SCORES:", result["semantic_scores"])
    print("HYBRID SCORES:", result["hybrid_scores"])