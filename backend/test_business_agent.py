
from business_agent import business_analysis_agent


sample_content = """
The company generates recurring revenue from subscriptions.
The business has achieved a high net profit margin.
The organization is expanding its market share.
The company plans business expansion into new regions.
The organization follows a subscription-based business model.
The company offers discounts through its pricing strategy.
The sales team improved the sales conversion rate.
The company received investment from external investors.
"""

result = business_analysis_agent(sample_content)

print("\nBUSINESS AGENT RESULTS")
print("=" * 60)

print("Agent:", result["agent"])
print("Total Findings:", result["total_findings"])

for index, finding in enumerate(result["findings"], start=1):
    print(f"\nFinding: {index}")
    print("Observation:", finding["observation"])
    print("Business Area:", finding["business_area"])
    print("Matched Keywords:", finding["matched_keywords"])
    print("Review Question:", finding["review_question"])
    print("Recommended Check:", finding["recommended_check"])
    print("Status:", finding["status"])

print("\nAgent Note:")
print(result["note"])
