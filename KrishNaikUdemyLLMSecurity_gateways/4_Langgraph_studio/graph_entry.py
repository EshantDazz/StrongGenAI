import sys
import os

from langgraph.graph.state import CompiledStateGraph

from agent.graph import AgentState

# Add the project root to sys.path so 'agent' is importable as a package.
# This makes relative imports inside agent/ resolve correctly without pip install -e .
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.graph import build_graph

graph: CompiledStateGraph[AgentState, None, AgentState, AgentState] = build_graph()
