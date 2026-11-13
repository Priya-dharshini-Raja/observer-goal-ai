
from goal_model import detect_goals

query = "Analyze website security vulnerabilities and authentication risks"

result = detect_goals(query)

print("User Query:", query)
print("Primary Goal:", result["primary_goal"])
print("Goal Weights:", result["goal_weights"])
