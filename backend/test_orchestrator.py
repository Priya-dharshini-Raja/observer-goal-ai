
from orchestrator import adaptive_analysis, generate_observer_report
import json


# Sample content to analyze
content = (
    "The website uses authentication. "
    "The company earns revenue through subscriptions. "
    "The application uses a REST API. "
    "The website has simple navigation."
)

# Observer's analytical goal
query = "Give me a general overview of this content"


# Step 1: Run adaptive analysis
result = adaptive_analysis(content, query)

print("Detected goal:", result["goal_detection"])
print("Selected agent count:", result["selected_agent_count"])

print("\nAnalysis results:")
for analysis in result["analysis_results"]:
    print(analysis)


# Step 2: Debug the business agent's original findings
print("\nDEBUG - Business agent findings:")
for item in result["analysis_results"]:
    if item["goal"] == "business":
        for finding in item["analysis"]["findings"]:
            print(repr(finding["observation"]))


# Step 3: Generate the unified observer report
report = generate_observer_report(result)

print("\nUnified Observer Report:")
print(json.dumps(report, indent=2, ensure_ascii=False))


# Step 4: Display each observation separately for easier checking
print("\nDEBUG - Unified report observations:")
for finding in report["findings"]:
    print(f"{finding['goal']}: {finding['observation']!r}")
