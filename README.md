# googleAds-MultiAgent-KPI-research-campaign-planner
This aims to create a multi agents orchestrate together to provide appropriate campaign planner for the provided KPI  from Marketer which in turn do an insight,research with previous data from google bigquery via MCP and provide quick value realization to achive the Targeted KPI using Google ADK framework

📘 Detailed Implementation Guide

This section provides an in-depth technical explanation of how the KPI Achievement Engine is implemented using the ADK multi-agent architecture, including its agents, tools, data access layer, and orchestrator logic.

🔍 1. Agent: InsightsAgent

The InsightsAgent is the first agent (L1) in the multi-agent pipeline.
Its goal is to establish a baseline understanding of KPI performance, identify current trends, detect gaps, and prepare data for deeper diagnosis in later stages.

✅ Responsibilities

Read the KPI target (metric, current value, desired target, timeframe).

Query BigQuery for:

Current KPI performance

Campaign-level breakdown

Supporting metrics (CTR, CPC, CVR, ROAS, Cost)

Perform first-level analysis:

What’s working?

What’s underperforming?

Which campaigns contribute most to the gap?

Produce structured output:

current_state

gap_analysis

key_insights

risk_areas

opportunities

This output becomes an A2A Artifact, consumed by the ResearchAgent.

🔧 Implementation Overview

The agent is implemented using:

class InsightsAgent:
    def __init__(self, client, bq_tools):
        self.client = client
        self.bq_tools = bq_tools

🔹 Prompt Construction

The orchestrator sends a prompt using build_insights_prompt(kpi_target):

You are an expert data analyst. Analyze the current state of this KPI.
...
Tasks:
1. Use BigQuery queries to get detailed current metrics
2. Analyze campaign-level contributions
3. Identify key insights and risks
4. Provide structured JSON output

🔹 Agent Workflow (Pseudocode)

Receive the prompt

Use the Gemini model to request data or tools

When a function_call is requested, route it to BigQuery helpers

Repeat until model returns a final JSON

Validate & return the structured insights

This establishes a clean data-driven foundation for subsequent agents.

🛠 2. Tool Definitions

The system uses Function Calling Tools so that the LLM can request data programmatically.

Example Tool Definition:
AgentTool(
    name="get_current_kpi_metrics",
    description="Fetches current KPI values from BigQuery",
    func=self.bq_tools.get_kpi_current_value
)

Typical Tools Exposed:
Tool Name	Purpose
get_current_kpi_metrics	Retrieves KPI metric values (Cost, Revenue, ROAS, etc.)
get_campaign_breakdown	Provides performance by campaign
get_time_series_trends	Historical metric trends
analyze_campaign_efficiency	Compares cost vs conversions efficiency
Why use Tools?

Ensures validated SQL execution

Fully auditable queries

Reduces LLM hallucination

Aligns with ADK Tooling design patterns

Each agent only receives tools relevant to its stage, following Principle of Least Privilege.

🗄 3. BigQuery Interface Methods

These methods live in a separate utility class, keeping SQL logic isolated and maintainable.

Example Class Definition:
class BigQueryTools:
    def __init__(self, client, project_id, dataset_id, table_id):
        self.client = client
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.table_id = table_id

🔹 Method 1: get_kpi_current_value()

Retrieves explicit numeric measures such as:

Impressions

Clicks

Cost

Conversions

Revenue

ROAS

CPC / CPM / CVR

SQL Example:

SELECT
  SUM(cost) AS total_cost,
  SUM(conversions) AS conversions,
  SUM(revenue) AS total_revenue,
  SAFE_DIVIDE(SUM(revenue), SUM(cost)) AS roas
FROM `project.dataset.table`

🔹 Method 2: get_campaign_performance()

Used to identify:

Best / worst campaign

Efficiency gaps

Budget waste

Underperforming segments

SQL Example:

SELECT
  campaign_name,
  SUM(cost) AS cost,
  SUM(conversions) AS conversions,
  SAFE_DIVIDE(SUM(revenue), SUM(cost)) AS roas
FROM `project.dataset.table`
GROUP BY campaign_name
ORDER BY cost DESC

🔹 Method 3: get_time_series_data()

Used in L2 research (trend analysis):

SELECT
  date,
  SUM(cost) AS cost,
  SUM(revenue) AS revenue,
  SAFE_DIVIDE(SUM(revenue), SUM(cost)) AS roas
FROM `project.dataset.table`
GROUP BY date
ORDER BY date ASC

Why this abstraction is powerful

Decouples agents from raw SQL

Makes pipeline testable

Enables partial swap-out (mock BQ during offline tests)

Secure: Only known SQL patterns are executed

Works with ADK’s NL2SQL when necessary

🧠 4. Final Orchestrator Logic

The KPIAnalysisOrchestrator controls the full multi-agent flow:

Manages A2AContext events

Tracks execution duration

Builds prompts for each agent

Maintains in-memory structured state

Produces final consolidated strategy

🔍 Orchestrator Flow
Step 1 — Insights Stage
insights_prompt = build_insights_prompt(kpi_target)
insights_json = self.insights_agent.analyze_kpi(insights_prompt)
self.context.log_artifact("Insights", insights_json)


Outputs:

current_state

gap_analysis

key_insights

opportunities

Step 2 — Deep Research Stage
research_prompt = build_research_prompt(insights, kpi_target)
research_json = self.research_agent.research_opportunities(research_prompt)
self.context.log_artifact("ResearchSummary", research_json)


Outputs:

trends

efficiency_gaps

optimization_opportunities

hypotheses

Step 3 — Planning Stage
planning_prompt = build_planning_prompt(insights, research, kpi_target)
plan_json = self.planning_agent.create_action_plan(planning_prompt)
self.context.log_artifact("StrategyPlan", plan_json)


Outputs:

quick wins

medium effort strategy

high effort roadmap

metrics to track

timeline

executive summary

📦 Final Output

The orchestrator returns a fully structured JSON:

{
  "insights": { ... },
  "research": { ... },
  "strategy_plan": { ... },
  "timing": {
    "insights_ms": 1200,
    "research_ms": 1900,
    "planning_ms": 1400,
    "total_ms": 4500
  }
}


Perfect for:

Dashboards

Notebooks

Slack/Email alerts

A/B experiments

Automated optimization loops
