# ============================================================================
# ADK KPI ACHIEVEMENT ENGINE: Multi-Agent System for Google Ads Analysis
#
# This script implements the production-ready architecture using ADK principles
# and Pydantic for robust A2A (Agent-to-Agent) communication.
#
# NOTE: If ADK libraries are not installed, the code uses Mock Classes to
# successfully demonstrate the architecture and orchestration flow.
# ============================================================================
import os
import json
from typing import Dict, List, Any
import logging
from pydantic import BaseModel, Field

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- ADK and Google Cloud Imports/Fallbacks ---
try:
    # Standard ADK Imports
    from google.adk.agents.llm_agent import Agent
    from google.adk.tools import AgentTool
    from google.adk.tools.bigquery import (
        BigQueryToolset,
        BigQueryCredentialsConfig
    )
    from google.adk.tools.bigquery.config import BigQueryToolConfig, WriteMode
    from google.adk.tools.function_calling import FunctionDeclaration
    import google.auth
    print("ADK libraries successfully imported. Running with live ADK tools.\n")

except ImportError:
    print("WARNING: ADK or other required libraries not found. Using Mock ADK for successful demo run.\n")
    
    # --- FALLBACK: Mock ADK Classes (SYNTAX CORRECTED) --- 
    class Agent:
        def __init__(self, **kwargs): 
            self.name = kwargs.get('name', 'MockAgent')
        def run(self, prompt):
            # Simulation of agent output for local testing without ADK/BQ
            if 'Insights_Agent' in self.name:
                 return AnomalyReport(campaign_id="CAM_1234", metric_name="ROAS", deviation_value="-25% lower than target 4.5", hypotheses=["Device type (Mobile/Desktop) bias.", "Geographic region underperformance (e.g., California/New York).", "Budget allocation imbalance."])
            if 'Deep_Research_Agent' in self.name:
                 return ResearchSummaryArtifact(root_cause="Mobile bidding strategy is set too low for high-value regions (US East Coast) leading to suppressed high-value conversions.", supporting_data="SELECT AVG(ROAS) FROM ads_performance WHERE device='mobile' AND region IN ('NY', 'MA') -- shows 3.1 ROAS vs 5.5 for Desktop.", actionable_summary="Confirmed root cause related to mobile bid strategy and geographic segmentation of conversion value.")
            if 'Planning_Agent' in self.name:
                # The mock Planning Agent returns the final JSON string directly
                return json.dumps({
                    "overall_strategy": "Immediate tactical shift to re-allocate mobile bids in underperforming high-value US regions, followed by a strategic ad copy and landing page refinement.",
                    "estimated_timeline": "3 weeks",
                    "quick_wins": [
                        {"title": "Increase Mobile Bid Multiplier", "description": "Raise the mobile bid multiplier by 25% in high-gap regions (NY, MA, FL). Effort: 1 day.", "effort_level": "low", "expected_impact": "high", "implementation_steps": ["Apply bid adjustment in Google Ads UI.", "Monitor for 7 days."]}
                    ],
                    "medium_effort": [
                        {"title": "A/B Test New Mobile Ad Copy", "description": "Test new ad copy emphasizing mobile-specific value propositions. Effort: 1 week.", "effort_level": "medium", "expected_impact": "medium", "implementation_steps": ["Create 3 new responsive search ads.", "Set up 14-day A/B test."]}
                    ],
                    "high_effort": [
                        {"title": "Automate Smart Bidding Migration", "description": "Transition the campaign to 'Maximize Conversion Value with target ROAS' to better capture regional value differences. Effort: 2 weeks.", "effort_level": "high", "expected_impact": "transformational", "implementation_steps": ["Review conversion actions quality.", "Migrate bidding strategy and set ROAS target to 4.2."]}
                    ],
                })
            return ""
        
    # Standard Python class definition for mock objects
    class BigQueryToolset:
        def __init__(self, **kwargs):
            pass
    class BigQueryCredentialsConfig:
        def __init__(self, **kwargs):
            pass
    class BigQueryToolConfig:
        def __init__(self, **kwargs):
            pass
    class WriteMode:
        ALLOWED = "ALLOWED"
    class FunctionDeclaration:
        def __init__(self, **kwargs):
            pass
    
    class MockAuth:
        def default(self):
            # Mocks the return structure of google.auth.default()
            return (None, "mock-project-id")
    # Provide a minimal mock 'google' object with an 'auth' attribute
    import types
    google = types.SimpleNamespace(auth=MockAuth())


# ============================================================================
# 2. DATA MODELS (A2A Contracts - Pydantic)
# ============================================================================

class AnomalyReport(BaseModel):
    """Structured report defining a specific KPI gap or anomaly (Insights Agent Output)."""
    campaign_id: str = Field(..., description="The ID of the underperforming Google Ads Campaign.")
    metric_name: str = Field(..., description="The KPI metric (e.g., ROAS, Conversion Rate) showing the gap.")
    deviation_value: str = Field(..., description="The magnitude and direction of the deviation (e.g., '-1.2% lower').")
    hypotheses: List[str] = Field(..., description="Initial high-level guesses (e.g., device split, geo bias) for L2 research.")

class ResearchSummaryArtifact(BaseModel):
    """Structured artifact containing confirmed causal links (Deep Research Agent Output)."""
    root_cause: str = Field(..., description="The confirmed primary causal factor for the performance gap.")
    supporting_data: str = Field(..., description="The raw data/SQL results that verify the root cause.")
    actionable_summary: str = Field(..., description="A summary of the technical findings ready for strategic planning.")

# ============================================================================
# 3. BIGQUERY TOOLSET AND NL2SQL FUNCTION DECLARATION CONFIGURATION
# ============================================================================

# --- USER CONFIGURATION REQUIRED (Edit for Live Data Access) ---
PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "your-gcp-project-id-HERE") # <-- **EDIT THIS**
DATASET_ID = "google_ads_data" # <-- **EDIT THIS if different**
TABLE_NAME = "ads_performance" # <-- **EDIT THIS**
FULLY_QUALIFIED_TABLE = f"`{PROJECT_ID}.{DATASET_ID}.{TABLE_NAME}`"

# 3.1. Configure the ADK BigQuery Toolset
bigquery_toolset = BigQueryToolset(
    config=BigQueryToolConfig(
        write_mode=WriteMode.ALLOWED,
        application_name='kpi-ads-research-engine'
    ),
    credentials_config=BigQueryCredentialsConfig(
        credentials=google.auth.default()[0]
    )
)

# 3.2. Define the Precise NL2SQL Function Declaration
execute_sql_declaration = FunctionDeclaration(
    name="execute_bigquery_sql",
    description=f"""Tool used exclusively for deep quantitative analysis on Google Ads performance data in BigQuery. 
    The model must generate a SQL query on a single line that leverages analytical functions (e.g., joins, window functions) to test causality. 
    IMPORTANT: Always use the fully qualified dataset and table name: {FULLY_QUALIFIED_TABLE} to ensure execution succeeds.""",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The complete, single-line SQL query to execute against BigQuery."
            }
        },
        "required": ["query"]
    }
)

# ============================================================================
# 4. AGENT DEFINITIONS (ADK Agents)
# ============================================================================

# 4.1. Insights Agent (L1)
insights_agent = Agent(
    model="gemini-2.5-flash",
    name="Insights_Agent",
    description="Analyzes current Google Ads performance data in BigQuery and outputs a structured AnomalyReport.",
    instruction=f"""You are a KPI Monitoring Specialist. Your role is to calculate current performance metrics from the BigQuery data ({FULLY_QUALIFIED_TABLE}) and compare them to the user's target KPI.
    1. **Prioritize Schema:** Use your BigQuery tools to understand the schema first, as an expert data analyst.
    2. **Identify Gap:** Identify the top 3 dimensions (e.g., Campaign ID, Geo, Device) driving the largest negative deviation from the target.
    3. **Output Strictly:** Output your findings **strictly** as a JSON object matching the Pydantic structure for AnomalyReport. \n    4. **No Other Text:** Do NOT output any other text or reasoning.
    """,
    tools=[bigquery_toolset], 
    structured_output=AnomalyReport 
)

# 4.2. Deep Research Agent (L2)
research_agent = Agent(
    model="gemini-2.5-pro", 
    name="Deep_Research_Agent",
    description="Conducts deep, iterative data analysis to find the root cause of the performance gap.",
    instruction=f"""You are a Causal Data Research Specialist. Your input is an AnomalyReport (A2A Task Card) from the Insights Agent.
    1. **Generate SQL:** Use the 'execute_bigquery_sql' tool and the hypotheses to generate and execute precise SQL queries to retrieve quantitative evidence.
    2. **Hypothesis Test:** Test the hypotheses by generating complex BigQuery SQL (using window functions, joins, etc., and always using the fully qualified table name: {FULLY_QUALIFIED_TABLE}).
    3. **Synthesize:** Compile the evidence (SQL results, causal links) into a comprehensive ResearchSummaryArtifact object for the Planning Agent.
    """,
    tools=[bigquery_toolset, execute_sql_declaration],
    structured_output=ResearchSummaryArtifact 
)

# 4.3. Planning Agent (L3)
planning_agent = Agent(
    model="gemini-2.5-flash", 
    name="Planning_Agent",
    description="Translates technical findings into a prioritized, actionable business strategy.",
    instruction=f"""You are a Strategic Planning Expert. Your input is the Research Summary Artifact (data evidence) from the Deep Research Agent.
    Your sole task is to synthesize the confirmed root cause and supporting data into an actionable strategy report.
    The final output **must** be a single JSON object (no other text) containing three prioritized categories of recommendations:
    1. **QUICK WINS** (Low Effort, Immediate Impact)
    2. **MEDIUM EFFORT** (Moderate Effort, Significant Impact)
    3. **HIGH EFFORT** (High Effort, Transformational Impact)
    Each recommendation should include a title, detailed description, effort_level, expected_impact, and implementation_steps.
    """,
    tools=[], 
)

# ============================================================================
# 5. ADK ORCHESTRATOR AND EXECUTION
# ============================================================================

def run_kpi_engine(kpi_target_prompt: str) -> Dict[str, Any]:
    """Executes the three-stage multi-agent workflow (Orchestrator)."""
    
    orchestration_trace = {"steps": {}, "status": "success"}

    initial_prompt = f"Assess current ROAS against a target of 4.5 and identify the top campaign holding back performance. Target timeframe: 30 days. Initial KPI goal: {kpi_target_prompt}"
    
    # --- STAGE 1: Insights Generation (L1) ---
    logger.info("\n--- STAGE 1: INSIGHTS AGENT RUNNING (KPI Monitoring) ---")
    logger.info(f"Initial Prompt: {initial_prompt}")
    
    try:
        anomaly_report_object = insights_agent.run(initial_prompt)
        # Support both Pydantic v2 (model_dump) and v1 (dict)
        if hasattr(anomaly_report_object, "model_dump"):
            anomaly_dict = anomaly_report_object.model_dump()
        elif hasattr(anomaly_report_object, "dict"):
            anomaly_dict = anomaly_report_object.dict()
        else:
            # If the agent returned a raw dict/string, normalize it
            anomaly_dict = anomaly_report_object if isinstance(anomaly_report_object, dict) else {}
        anomaly_data_json = json.dumps(anomaly_dict, indent=2)
        
        orchestration_trace["steps"]["insights"] = {
            "data": json.loads(anomaly_data_json),
            "status": "completed",
            "next_input": anomaly_data_json
        }
        logger.info(f"L1 Output (AnomalyReport) successfully generated and validated:\n{anomaly_data_json}")

    except Exception as e:
        logger.error(f"STAGE 1 FAILED: {e}")
        orchestration_trace["status"] = "failed_insights"
        return orchestration_trace

    # --- STAGE 2: Deep Research (L2) ---
    logger.info("\n--- STAGE 2: DEEP RESEARCH AGENT RUNNING (Causal Analysis) ---\n")
    
    try:
        research_artifact_object = research_agent.run(anomaly_data_json)
        # Support both Pydantic v2 (model_dump) and v1 (dict)
        if hasattr(research_artifact_object, "model_dump"):
            research_dict = research_artifact_object.model_dump()
        elif hasattr(research_artifact_object, "dict"):
            research_dict = research_artifact_object.dict()
        else:
            research_dict = research_artifact_object if isinstance(research_artifact_object, dict) else {}
        research_artifact_json = json.dumps(research_dict, indent=2)

        orchestration_trace["steps"]["research"] = {
            "data": json.loads(research_artifact_json),
            "status": "completed",
            "next_input": research_artifact_json
        }
        logger.info(f"L2 Output (ResearchSummaryArtifact) successfully generated:\n{research_artifact_json}")

    except Exception as e:
        logger.error(f"STAGE 2 FAILED (Check ADK/NL2SQL logs): {e}")
        orchestration_trace["status"] = "failed_research"
        return orchestration_trace
        
    # --- STAGE 3: Strategic Planning (L3) ---
    logger.info("\n--- STAGE 3: PLANNING AGENT RUNNING (Strategy Synthesis) ---\n")
    
    try:
        final_plan_text = planning_agent.run(research_artifact_json)
        final_plan = json.loads(final_plan_text)
        
        orchestration_trace["steps"]["planning"] = {
            "data": final_plan,
            "status": "completed"
        }

    except Exception as e:
        logger.error(f"STAGE 3 FAILED: {e}")
        orchestration_trace["status"] = "failed_planning"
        return orchestration_trace

    logger.info("\n--- FINAL STRATEGIC PLAN GENERATED ---")
    return orchestration_trace

# --- Main Execution Block ---

# 1. Setup Authentication Check (best practice for ADK/GCP)
try:
    _, project_id = google.auth.default()
    logger.info(f"Authentication check passed for project: {project_id}")
except Exception as e:
    logger.error(f"Authentication failed (this is OK for a mock-run demo): {e}")
    
# 2. Execute the full engine with a sample KPI goal
initial_kpi_target = "I need to increase our quarter-over-quarter ROAS by 20% in the next 30 days for our US campaigns."

print("\n" + "*" * 80)
print(f"STARTING KPI ACHIEVEMENT ENGINE FOR GOAL: {initial_kpi_target}")
print("*" * 80)

final_report_data = run_kpi_engine(initial_kpi_target)

# 3. Print Final Summary (Structured Output)
if final_report_data["status"] == "success":
    plan = final_report_data["steps"]["planning"]["data"]
    
    print("\n" + "=" * 80)
    print("FINAL ANALYSIS AND STRATEGY REPORT")
    print("=" * 80)
    
    print(f"\n\nOVERALL STRATEGY: {plan.get('overall_strategy', 'N/A')}")
    print(f"ESTIMATED TIMELINE: {plan.get('estimated_timeline', 'N/A')}")
    
    print("\n" + "-" * 30)
    print(f"\n--- ⚡ Quick Wins ({len(plan.get('quick_wins', []))} Recommendations) ---")
    print("-" * 30)
    for rec in plan.get("quick_wins", [])[:3]:
        print(f"  • **{rec.get('title', 'N/A')}**: {rec.get('description', 'N/A')}")
    
    print("\n" + "-" * 30)
    print(f"--- 📈 Medium Effort ({len(plan.get('medium_effort', []))} Recommendations) ---")
    print("-" * 30)
    for rec in plan.get("medium_effort", [])[:3]:
        print(f"  • **{rec.get('title', 'N/A')}**: {rec.get('description', 'N/A')}")
        
    print("\n" + "-" * 30)
    print(f"--- 🚀 High Effort ({len(plan.get('high_effort', []))} Recommendations) ---")
    print("-" * 30)
    for rec in plan.get("high_effort", [])[:3]:
        print(f"  • **{rec.get('title', 'N/A')}**: {rec.get('description', 'N/A')}")
        
else:
    print(f"\nAgent orchestration failed during stage: {final_report_data['status']}. Check logs above for details.")
