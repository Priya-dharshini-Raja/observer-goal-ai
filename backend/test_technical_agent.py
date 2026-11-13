
from technical_agent import technical_analysis_agent


content = """
The application uses a REST API.
The system follows a microservices architecture.
Customer information is stored in a MySQL database.
The application experiences high response time.
The platform supports multiple concurrent users.
The system integrates with an external payment gateway.
"""


result = technical_analysis_agent(content)


print("\nTECHNICAL AGENT RESULTS")
print("=" * 60)

print("Agent:", result["agent"])
print("Total Findings:", result["total_findings"])

for index, finding in enumerate(result["findings"], start=1):

    print("\nFinding:", index)

    print("Observation:", finding["observation"])

    print("Technical Area:", finding["technical_area"])

    print("Matched Keywords:", finding["matched_keywords"])

    print("Review Question:", finding["review_question"])

    print("Recommended Check:", finding["recommended_check"])

    print("Status:", finding["status"])

print("\nAgent Note:")
print(result["note"])
