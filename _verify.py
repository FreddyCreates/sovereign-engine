import sys
sys.path.insert(0, "python/intelligence")

from capabilities import CapabilityRunner
r = CapabilityRunner()
print(f"Capabilities: {len(r.list_capabilities())}")

from future_ai import FUTURE_AI_REGISTRY
print(f"Future AI: {len(FUTURE_AI_REGISTRY)}")

from protocols_registry import ProtocolRegistry
pr = ProtocolRegistry()
print(f"Protocols: {len(pr.list_all())}")

from research_papers import PaperRegistry
rp = PaperRegistry()
print(f"Papers: {len(rp.list_all())}")

from master_index import MasterIndex
mi = MasterIndex()
total = mi.stats()["TOTAL"]
print(f"Index: {total}")

from character_ai import CharacterRegistry
cr = CharacterRegistry()
cr.load_agents_dir()
print(f"Agents: {len(cr.agents)}")

print("ALL MODULES OK")
