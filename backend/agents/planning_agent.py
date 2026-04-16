from __future__ import annotations

import json
from typing import Any, List, Dict
from backend.core.llm_client import get_llm_client

PLANNING_PROMPT = """
You are the Kortex Planning Agent. Your goal is to solve a user query by deciding which tools to use and in what order.
You operate in a loop: Thought -> Action -> Observation -> Thought...

Available Tools:
1. doc_search(query): Searches internal SOPs and technical documentation. Use for "how-to" or configuration questions.
2. ticket_search(query): Searches historical IT support tickets. Use for "errors", "incidents", or "past issues".
3. synthesize(query, contexts): Generates a final answer based on retrieved contexts.
4. validate(answer, contexts): Validates the answer for confidence and faithfulness.
5. summarize(contexts): Provides a concise summary of the retrieved information. Use when the user asks for a "summary" or when there is too much information.
6. check_duplicates(query): Checks if a similar issue has been reported in historical tickets. Use this to flag duplicate support tickets.

Rules:
- If the query is complex, you can call multiple search tools.
- Every response must follow this format:
Thought: [Your reasoning about what to do next]
Action: [tool_name]
Action Input: [input_parameters]

If you have a final answer that has been validated, use:
Final Answer: [The actual answer]

User Query: {query}
{history}
"""

class PlanningAgent:
    def __init__(self) -> None:
        self.client = get_llm_client()

    def plan_next_step(self, query: str, history: List[str]) -> Dict[str, Any]:
        formatted_history = "\n".join(history)
        prompt = PLANNING_PROMPT.format(query=query, history=formatted_history)
        
        try:
            response = self.client.generate(prompt, temperature=0.1)
            return self._parse_response(response)
        except Exception as e:
            return {"thought": f"Error in planning: {e}", "action": "error"}

    def _parse_response(self, response: str) -> Dict[str, Any]:
        lines = response.strip().split('\n')
        result = {"thought": "", "action": None, "action_input": None, "final_answer": None}
        
        for line in lines:
            if line.startswith("Thought:"):
                result["thought"] = line.replace("Thought:", "").strip()
            elif line.startswith("Action:"):
                result["action"] = line.replace("Action:", "").strip()
            elif line.startswith("Action Input:"):
                result["action_input"] = line.replace("Action Input:", "").strip()
            elif line.startswith("Final Answer:"):
                result["final_answer"] = line.replace("Final Answer:", "").strip()
                
        return result
