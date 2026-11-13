
from ux_agent import ux_analysis_agent


sample_content = """
The website focuses on usability and user satisfaction.
The application provides simple navigation menus.
The website supports screen reader and keyboard navigation accessibility.
The platform follows consistent user interface design.
The website uses responsive design for mobile devices.
The application improves readability through appropriate font size.
"""

result = ux_analysis_agent(sample_content)

print("\nUX AGENT RESULTS")
print("=" * 60)

print("Agent:", result["agent"])
print("Total Findings:", result["total_findings"])

for index, finding in enumerate(result["findings"], start=1):
    print(f"\nFinding: {index}")
    print("Observation:", finding["observation"])
    print("UX Area:", finding["ux_area"])
    print("Matched Keywords:", finding["matched_keywords"])
    print("Review Question:", finding["review_question"])
    print("Recommended Check:", finding["recommended_check"])
    print("Status:", finding["status"])

print("\nAgent Note:")
print(result["note"])
