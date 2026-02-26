def generate_pov(user:str, need:str, insight:str) -> str:
 user = (user or '').strip
 need = (need or '').strip
 insight = (insight or '').strip
 if not user or not need or not insight:
 return ''
 return f"{user} needs a way to {need} because {insight}."
def generate_hmw_from_pov(pov: str) -> list:
 if not pov:
 return
 # Simple angles: simplify, accelerate, clarify
 return [
 f"How might we simplify the path so that {pov}",
 f"How might we accelerate progress so that {pov}",
 f"How might we clarify key decisions so that {pov}",
 ]