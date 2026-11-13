
from orchestrator import adaptive_analysis


# Content to be analysed
content = """
The website uses authentication and password protection.
The company earns revenue through subscription sales.
The application uses a REST API and database architecture.
The website provides simple navigation and usability.
"""


# Test different observer goals
test_queries = [
    ("Security", "Analyze security vulnerabilities and authentication"),
    ("Business", "Analyze company revenue and profit"),
    ("Technical", "Review the API architecture and database"),
    ("User Experience", "Evaluate website usability and navigation"),
    ("General", "Give me a general overview of this website")
]


for test_name, query in test_queries:

    print("\n" + "=" * 60)
    print("TEST:", test_name)
    print("QUERY:", query)

    result = adaptive_analysis(content, query)

    print("\nDetected Goal:")
    print(result["goal_detection"]["primary_goal"])

    print("\nSelected Agent Count:")
    print(result["selected_agent_count"])

    print("\nSelected Agents:")

    for agent in result["analysis_results"]:
        print(
            agent["goal"],
            "| Weight:",
            agent["goal_weight"]
        )
