# GoogleAds-MultiAgent-KPI-research-campaign-planner
This aims to create a multi agents orchestrate together to provide appropriate campaign planner for the provided KPI  from Marketer which in turn do an insight,research with previous data from google bigquery via MCP and provide quick value realization to achive the Targeted KPI using Google ADK framework

# 📘 KPI Achievement Engine  
### **A Multi-Agent ADK Architecture for Google Ads KPI Diagnostics & Strategy Planning**

---

## 📖 Overview

The **KPI Achievement Engine** is a **multi-agent system** built using Google’s **ADK (Agent Developer Kit)** to analyze Google Ads performance data, identify root causes behind KPI gaps, and generate a structured strategy plan.

The system uses:

- Multi-Agent Pipeline  
- A2A Context Logging  
- BigQuery Data Access  
- Function Calling Tools  
- Structured JSON Responses  
- Pydantic Models  

This README documents the **detailed implementation** behind each part of the engine.

---

# 🔍 1. Agent: InsightsAgent

The **InsightsAgent** is **Stage 1 (L1)** of the pipeline.

Its goal:  
👉 *Understand the KPI’s current state, quantify the performance gap, detect anomalies, and surface first-level insights.*

---

### ✔ Responsibilities

- Retrieve **current KPI performance**
- Analyze **campaign-level contributions**
- Highlight **gaps and inefficiencies**
- Identify **risks** & **opportunities**
- Generate structured **JSON insights artifact**

---

### ✔ Prompt Structure

The orchestrator generates an insights prompt such as:

```
You are an expert data analyst. Analyze the current state of this KPI.

Tasks:
1. Query BigQuery for current KPI metrics
2. Analyze campaign-level performance
3. Identify insights, risks, and opportunities
4. Provide JSON output with:
   - current_state
   - gap_analysis
   - key_insights
   - risk_areas
   - opportunities
```

---

### ✔ Internal Logic (Simplified)

```python
insights_raw = insights_agent.run(insights_prompt)
insights_dict = json.loads(insights_raw)
```

The outcome becomes:

- First A2A artifact  
- Input to ResearchAgent  

---

# 🛠 2. Tool Definitions

Tools enable the LLM to **call real backend functions** (BigQuery queries).

Tools follow ADK’s function-calling syntax.

---

### ✔ Example Tool Mapping

```python
AgentTool(
    name="get_current_kpi_metrics",
    description="Fetches current KPI values from BigQuery",
    func=self.bq_tools.get_kpi_current_value
)
```

---

### ✔ Tools Used in System

| Tool Name | Purpose |
|----------|---------|
| get_current_kpi_metrics | Fetch KPI summary |
| get_campaign_breakdown | Campaign-level data |
| get_time_series_trends | Trend & seasonality check |
| analyze_campaign_efficiency | High-cost vs high-return |
| execute_bigquery_sql | NL2SQL dynamic query execution |

---

### ✔ Why Tools Matter

Tools allow:

- Accurate BigQuery execution  
- Zero SQL hallucination  
- Auditable deterministic logic  
- Secure prompts  
- Modular agent design  

---

# 🗄 3. BigQuery Interface Methods

All SQL logic is isolated inside `BigQueryTools`.

This enables:

- Clean code  
- Testability  
- Reusability  
- Control over data access  

---

## ✔ Structure

```python
class BigQueryTools:
    def __init__(self, client, project_id, dataset_id, table_id):
        ...
```

---

### 🔹 Method: get_kpi_current_value()

Purpose: Retrieve KPI’s current metrics.

SQL Example:

```sql
SELECT
  SUM(cost) AS cost,
  SUM(conversions) AS conversions,
  SUM(revenue) AS revenue,
  SAFE_DIVIDE(SUM(revenue), SUM(cost)) AS roas
FROM `project.dataset.table`
```

---

### 🔹 Method: get_campaign_performance()

Purpose: Identify campaign-level efficiencies.

SQL Example:

```sql
SELECT
  campaign_name,
  SUM(cost) AS cost,
  SUM(conversions) AS conversions,
  SAFE_DIVIDE(SUM(revenue), SUM(cost)) AS roas
FROM `project.dataset.table`
GROUP BY campaign_name
ORDER BY cost DESC
```

---

### 🔹 Method: get_time_series_data()

Purpose: Detect seasonality or trending behavior.

SQL:

```sql
SELECT
  date,
  SUM(cost) AS cost,
  SUM(revenue) AS revenue,
  SAFE_DIVIDE(SUM(revenue), SUM(cost)) AS roas
FROM `project.dataset.table`
GROUP BY date
ORDER BY date ASC
```

---

### ✔ Why It’s Powerful

- LLM never writes raw SQL (unless NL2SQL is explicitly used)  
- Stable, validated data retrieval  
- Works offline with mock data  
- Matches enterprise analytics patterns  

---

# 🧠 4. Final Orchestrator Logic

The orchestrator controls the entire multi-agent pipeline:

### Insights → Research → Planning

It coordinates:

- Prompt building  
- Agent invocation  
- A2AContext logging  
- Memory state updates  
- Timing metrics  
- Final JSON output  

---

## ✔ Orchestrator Flow Details

### Step 1 — Insights Stage

```python
insights = insights_agent.analyze_kpi(insights_prompt)
context.log_artifact("Insights", insights)
```

Outputs include:

- KPI current state  
- Gap analysis  
- Opportunities  

---

### Step 2 — Deep Research Stage

```python
research = research_agent.research_opportunities(research_prompt)
context.log_artifact("ResearchSummary", research)
```

Outputs include:

- Data-driven recommendations  
- Trend patterns  
- Efficiency gaps  
- Hypotheses  

---

### Step 3 — Planning Stage

```python
plan = planning_agent.create_action_plan(planning_prompt)
context.log_artifact("StrategyPlan", plan)
```

Outputs include:

- Quick wins  
- Medium-effort recommendations  
- High-effort initiatives  
- Success metrics  
- Timeline  
- Executive summary  

---
