
from goal_model import detect_goals

from agents import security_analysis_agent
from business_agent import business_analysis_agent
from technical_agent import technical_analysis_agent
from ux_agent import ux_analysis_agent


def adaptive_analysis(content: str, user_query: str) -> dict:
    """
    Detect the observer's goal and execute relevant specialized agents.
    """

    # Step 1: Detect observer goal
    goal_result = detect_goals(user_query)

    primary_goal = goal_result["primary_goal"]
    goal_weights = goal_result["goal_weights"]

    # Step 2: Register specialized agents
    agents = {
        "security": security_analysis_agent,
        "business": business_analysis_agent,
        "technical": technical_analysis_agent,
        "user_experience": ux_analysis_agent,
    }

    # Step 3: Select agents based on observer goal
    if primary_goal == "general":
        selected_agents = list(agents.items())

    else:
        selected_agents = [
            (goal, agents[goal])
            for goal, weight in goal_weights.items()
            if goal in agents and weight > 0
        ]

    # Step 4: Execute selected agents
    results = []

    if selected_agents:

        if primary_goal == "general":
            agent_weight = 1.0 / len(selected_agents)

            for goal, agent_function in selected_agents:

                agent_result = agent_function(content)

                results.append({
                    "goal": goal,
                    "goal_weight": agent_weight,
                    "analysis": agent_result,
                })

        else:
            for goal, agent_function in selected_agents:

                weight = goal_weights[goal]

                agent_result = agent_function(content)

                results.append({
                    "goal": goal,
                    "goal_weight": weight,
                    "analysis": agent_result,
                })

    # Step 5: Return adaptive analysis
    return {
        "goal_detection": goal_result,
        "selected_agent_count": len(selected_agents),
        "analysis_results": results,
    }


def generate_observer_report(adaptive_result: dict) -> dict:
    """
    Combine specialist findings into one observer-specific report
    and group findings that share the same observation.
    """

    goal_detection = adaptive_result["goal_detection"]
    analysis_results = adaptive_result["analysis_results"]

    all_findings = []
    agent_summary = {}

    category_fields = {
        "security": "security_area",
        "business": "business_area",
        "technical": "technical_area",
        "user_experience": "ux_area",
    }

    # Step 1: Collect individual findings
    for result in analysis_results:

        analysis = result["analysis"]
        goal = result["goal"]
        goal_weight = result["goal_weight"]

        category_field = category_fields.get(goal)
        findings = analysis.get("findings", [])

        agent_summary[goal] = {
            "agent": analysis.get("agent", "unknown"),
            "goal_weight": goal_weight,
            "total_findings": len(findings),
        }

        if goal_weight >= 0.5:
            goal_importance = "high"
        elif goal_weight >= 0.3:
            goal_importance = "medium"
        else:
            goal_importance = "low"

        if goal_detection["primary_goal"] == "general":
            selection_reason = (
                "Selected to provide a general overview "
                "because no specialized goal was detected."
            )
        else:
            selection_reason = (
                "Selected because the observer's query matched "
                f"the {goal.replace('_', ' ')} goal."
            )

        for finding in findings:

            all_findings.append({
                "goal": goal,
                "goal_weight": goal_weight,
                "goal_importance": goal_importance,
                "agent": analysis.get("agent", "unknown"),
                "selection_reason": selection_reason,
                "observation": finding.get("observation", ""),
                "analysis_area": (
                    finding.get(category_field, [])
                    if category_field else []
                ),
                "matched_keywords": finding.get(
                    "matched_keywords", []
                ),

                # New: Include finding priority
                "priority": finding.get("priority", "medium"),

                "review_question": finding.get("review_question"),
                "recommended_check": finding.get(
                    "recommended_check"
                ),
                "status": finding.get(
                    "status", "requires_review"
                ),
            })

    # Step 2: Group findings by their observation
    grouped_findings = {}

    for finding in all_findings:

        observation = finding["observation"].strip()

        # Normalize text for grouping
        group_key = " ".join(observation.casefold().split())

        if not group_key:
            continue

        if group_key not in grouped_findings:

            grouped_findings[group_key] = {
                "observation": observation,
                "agents": [],
                "goals": [],
                "perspectives": [],
                "matched_keywords": [],
            }

        group = grouped_findings[group_key]

        if finding["agent"] not in group["agents"]:
            group["agents"].append(finding["agent"])

        if finding["goal"] not in group["goals"]:
            group["goals"].append(finding["goal"])

        # Preserve the complete individual agent finding,
        # including its priority.
        group["perspectives"].append(finding)

        for keyword in finding["matched_keywords"]:
            if keyword not in group["matched_keywords"]:
                group["matched_keywords"].append(keyword)

    # Step 3: Convert groups into a report-friendly list
    finding_groups = []

    for index, group in enumerate(
        grouped_findings.values(), start=1
    ):

        finding_groups.append({
            "group_id": index,
            "observation": group["observation"],
            "agents": group["agents"],
            "goals": group["goals"],
            "perspective_count": len(group["perspectives"]),
            "matched_keywords": group["matched_keywords"],
            "perspectives": group["perspectives"],
        })

    # Step 4: Return complete observer report
    return {
        "primary_goal": goal_detection["primary_goal"],
        "goal_weights": goal_detection["goal_weights"],
        "selected_agent_count": adaptive_result[
            "selected_agent_count"
        ],
        "agent_summary": agent_summary,
        "total_findings": len(all_findings),
        "total_finding_groups": len(finding_groups),
        "findings": all_findings,
        "finding_groups": finding_groups,
    }
