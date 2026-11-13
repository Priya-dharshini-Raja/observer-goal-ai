
from goal_model import (
    detect_goals,
    detect_goals_keyword,
    detect_goals_semantic
)


test_queries = [
    "Find ways this website could lose money and improve its earnings",

    "Check whether hackers can gain unauthorized access to this platform",

    "Find problems in the software architecture and backend infrastructure",

    "Determine whether visitors can easily navigate and understand this website",

    "Give me a general overview of this content",
    "Analyze authentication, encryption, and password protection",

    "Evaluate company profit, revenue, and sales performance",

    "Check database scalability and API response performance"
]


for query in test_queries:

    print("\n" + "=" * 65)

    print("OBSERVER QUERY:")
    print(query)

    print("\nKEYWORD-BASED RESULT:")
    print(detect_goals_keyword(query))

    print("\nSEMANTIC RESULT:")
    print(detect_goals_semantic(query))
