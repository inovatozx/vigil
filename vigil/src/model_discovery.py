from typing import List, Dict, Any
import httpx

class ModelDiscovery:
    def __init__(self):
        pass

    async def discover_ollama_models(self, ollama_base_url: str = "http://localhost:11434") -> List[Dict]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{ollama_base_url}/api/tags")
                response.raise_for_status()
                data = response.json()
                models = []
                for model_info in data.get("models", []):
                    models.append({
                        "provider": "ollama",
                        "name": model_info["name"],
                        "details": model_info
                    })
                return models
        except httpx.RequestError as e:
            print(f"Error discovering Ollama models: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"Error decoding Ollama response: {e}")
            return []

    async def discover_openai_models(self, openai_base_url: str = "https://api.openai.com/v1", api_key: str = None) -> List[Dict]:
        if not api_key:
            return []
        try:
            headers = {"Authorization": f"Bearer {api_key}"}
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{openai_base_url}/models", headers=headers)
                response.raise_for_status()
                data = response.json()
                models = []
                for model_info in data.get("data", []):
                    if model_info.get("id", "").startswith(("gpt", "dall-e", "whisper")):
                        models.append({
                            "provider": "openai",
                            "name": model_info["id"],
                            "details": model_info
                        })
                return models
        except httpx.RequestError as e:
            print(f"Error discovering OpenAI models: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"Error decoding OpenAI response: {e}")
            return []

    async def discover_all_models(self) -> List[Dict]:
        from core.config import get_settings
        settings = get_settings()

        all_models = []
        # Ollama
        all_models.extend(await self.discover_ollama_models(ollama_base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")))
        # OpenAI
        all_models.extend(await self.discover_openai_models(api_key=os.environ.get("OPENAI_API_KEY")))
        # Add other providers here
        return all_models
