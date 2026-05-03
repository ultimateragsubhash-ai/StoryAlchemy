"""LLM client for making API calls to MeshAPI using OpenAI SDK."""

import json
import re
from typing import Optional, Dict, Any, List
from openai import AsyncOpenAI
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for LLM API calls using OpenAI SDK."""
    
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.meshapi_api_key,
            base_url=settings.meshapi_base_url,
        )
        
    async def generate(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, str]] = None,
        stream: bool = False,
    ):
        """Generate completion from LLM using OpenAI SDK."""
        
        logger.info(f"LLM.generate called with model={model}, messages count={len(messages)}, stream={stream}")
        
        try:
            # Build kwargs dynamically
            kwargs = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "stream": stream,
            }
            
            if max_tokens:
                kwargs["max_tokens"] = max_tokens
                
            if response_format:
                kwargs["response_format"] = response_format
            
            logger.info(f"Calling OpenAI SDK with model={model}")
            
            response = await self.client.chat.completions.create(**kwargs)
            
            if stream:
                # Return the stream for the caller to iterate
                return response
            
            logger.info(f"LLM API response received successfully")
            
            # Convert OpenAI response to dict format
            return {
                "choices": [
                    {
                        "message": {
                            "role": response.choices[0].message.role,
                            "content": response.choices[0].message.content,
                        },
                        "finish_reason": response.choices[0].finish_reason,
                    }
                ],
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0,
                },
                "model": response.model,
            }
            
        except Exception as e:
            logger.error(f"LLM API error: {type(e).__name__}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def _clean_json_content(self, content: str) -> str:
        """Aggressively clean JSON content to handle LLM output quirks."""
        
        # Log raw content for debugging
        logger.debug(f"Raw LLM content before cleaning: {repr(content[:1000])}")
        
        # Step 1: Strip whitespace
        content = content.strip()
        
        # Step 2: Remove markdown code blocks
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        
        if content.endswith("```"):
            content = content[:-3]
        
        content = content.strip()
        
        # Step 3: Handle literal newlines (backslash-n) vs actual newlines
        content = content.replace('\\n', '\n')
        content = content.replace('\\t', ' ')
        content = content.replace('\\r', '')
        
        # Step 4: Normalize all whitespace around JSON structural characters
        content = re.sub(r'[\n\r\t\s]*"', '"', content)
        
        # Step 5: Remove any remaining control characters
        content = re.sub(r'[\x00-\x09\x0b-\x0c\x0e-\x1f]', '', content)
        
        # Step 6: Fix trailing commas in objects and arrays
        content = re.sub(r',\s*}', '}', content)
        content = re.sub(r',\s*]', ']', content)
        
        # Step 7: Fix multiple consecutive spaces
        content = re.sub(r'\s+', ' ', content)
        
        # Step 8: Restore proper JSON structure
        content = re.sub(r'":"', '": "', content)
        content = re.sub(r'",\s*"', '", "', content)
        
        logger.debug(f"Cleaned content: {repr(content[:1000])}")
        
        return content
    
    def _extract_json_with_regex(self, content: str) -> Optional[str]:
        """Extract JSON object from potentially malformed content using regex."""
        
        patterns = [
            r'\{[^{}]*"themes"[^{}]*\}',
            r'\{[^{}]*\}',
            r'\{.*\}',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                extracted = match.group(0)
                logger.debug(f"Regex extracted JSON: {repr(extracted[:500])}")
                return extracted
        
        return None
    
    def _parse_json_flexible(self, content: str) -> Optional[Dict[str, Any]]:
        """Try multiple strategies to parse JSON."""
        
        # Strategy 1: Direct parse
        try:
            result = json.loads(content)
            if isinstance(result, dict):
                return result
        except json.JSONDecodeError:
            pass
        
        # Strategy 2: Extract JSON with regex and parse
        extracted = self._extract_json_with_regex(content)
        if extracted:
            try:
                result = json.loads(extracted)
                if isinstance(result, dict):
                    return result
            except json.JSONDecodeError:
                pass
        
        # Strategy 3: Try to fix single quotes
        fixed = content.replace("'", '"')
        try:
            result = json.loads(fixed)
            if isinstance(result, dict):
                return result
        except json.JSONDecodeError:
            pass
        
        return None
    
    async def generate_json(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
        default_structure: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate JSON response from LLM with robust error handling."""
        
        logger.info(f"generate_json called with model={model}")
        
        if default_structure is None:
            default_structure = {
                "themes": ["general"], 
                "emotional_arc": "neutral", 
                "genre_hint": "general"
            }
        
        try:
            # Add JSON instruction to system message
            json_instruction = "Respond ONLY with valid JSON. No markdown, no explanation, just raw JSON."
            has_json_instruction = any(json_instruction in m.get("content", "") for m in messages)
            
            if not has_json_instruction:
                messages = [
                    {"role": "system", "content": json_instruction},
                    *[m for m in messages if m.get("role") != "system"],
                ]
            
            logger.info(f"Calling generate with {len(messages)} messages")
            
            response = await self.generate(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            logger.info(f"Got response from generate, extracting content...")
            
            # Safely extract content
            if not isinstance(response, dict):
                logger.error(f"Response is not a dict: {type(response)}")
                return default_structure
            
            choices = response.get("choices")
            if not choices or not isinstance(choices, list) or len(choices) == 0:
                logger.error(f"No choices in response: {response.keys()}")
                return default_structure
            
            message = choices[0].get("message", {}) if isinstance(choices[0], dict) else {}
            content = message.get("content", "")
            
            logger.info(f"LLM JSON response raw: {repr(content[:500])}")
            
            # Clean and parse
            cleaned = self._clean_json_content(content)
            result = self._parse_json_flexible(cleaned)
            
            if result is not None:
                logger.info(f"Successfully parsed JSON with keys: {list(result.keys())}")
                return result
            
            logger.error(f"Failed to parse JSON from LLM response")
            logger.error(f"Original content: {repr(content[:1000])}")
            logger.error(f"Cleaned content: {repr(cleaned[:1000])}")
            
            return default_structure
            
        except Exception as e:
            logger.error(f"generate_json error: {type(e).__name__}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return default_structure
    
    def estimate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost in USD for API call."""
        pricing = {
            "openai/gpt-4o": {"input": 0.005, "output": 0.015},
            "openai/gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
            "google/gemini-flash-1.5": {"input": 0.000075, "output": 0.0003},
            "google/gemini-pro-1.5": {"input": 0.0005, "output": 0.0015},
        }
        
        rates = pricing.get(model, pricing["openai/gpt-4o-mini"])
        input_cost = (input_tokens / 1000) * rates["input"]
        output_cost = (output_tokens / 1000) * rates["output"]
        
        return round(input_cost + output_cost, 6)


# Global client instance
llm_client = LLMClient()
