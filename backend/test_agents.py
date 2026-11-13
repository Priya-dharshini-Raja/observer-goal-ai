
from agents import security_analysis_agent

sample_content = """
The application uses multi-factor authentication for user login.
Administrators have role-based access control.
Customer personal information is protected using encryption.
The system stores passwords securely using password hashing.
The website may contain SQL injection vulnerabilities.
The application collects personal data from users.
The server uses HTTPS and TLS for secure communication.
"""

result = security_analysis_agent(sample_content)

print("\nSECURITY AGENT RESULTS")
print("=" * 60)

print("Agent:", result["agent"])
print("Total Findings:", result["total_findings"])

for index, finding in enumerate(result["findings"], start=1):
    print(f"\nFinding: {index}")
    print("Observation:", finding["observation"])
    print("Security Area:", finding["security_area"])
    print("Matched Keywords:", finding["matched_keywords"])
    print("Review Question:", finding["review_question"])
    print("Recommended Check:", finding["recommended_check"])
    print("Status:", finding["status"])

print("\nAgent Note:")
print(result["note"])
