from typing import List, Dict, Any

class PromptSecurity:
    def __init__(self):
        # Simple keyword-based detection for demonstration
        self.injection_keywords = [
            "ignore previous instructions",
            "disregard previous commands",
            "new instruction",
            "you are now",
            "as an AI, you must"
        ]

    def is_injection(self, prompt_text: str) -> bool:
        # Convert to lowercase for case-insensitive matching
        lower_prompt = prompt_text.lower()
        for keyword in self.injection_keywords:
            if keyword in lower_prompt:
                return True
        return False

    def sanitize_prompt(self, prompt_text: str) -> str:
        # Placeholder for more advanced sanitization techniques
        # For now, just a simple check
        if self.is_injection(prompt_text):
            return "I cannot process this request due to potential security concerns."
        return prompt_text

    def build_system_prompt(self, relevant_memories: List[Dict] = None) -> str:
        system_prompt = "You are Vigil, a helpful AI assistant. Your goal is to assist the user while maintaining ethical and secure interactions."
        if relevant_memories:
            memory_content = "\n".join([mem["content"] for mem in relevant_memories])
            system_prompt += f"\n\nHere is some relevant information from your memory:\n{memory_content}"
        return system_prompt
