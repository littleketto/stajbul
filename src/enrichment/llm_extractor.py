"""LLM-based structured data extraction using Google Gemini."""

import json
import logging
from typing import Any

from google import genai
from google.genai import types

from src.config.settings import get_settings
from src.models.schemas import ExtractedInternshipData
from .prompts import SYSTEM_PROMPT, build_user_prompt

logger = logging.getLogger(__name__)


class LLMExtractor:
    """Extracts structured internship data from job descriptions using Gemini."""
    
    def __init__(self, api_key: str | None = None, model: str | None = None):
        settings = get_settings()
        self.api_key = api_key or settings.gemini_api_key
        self.model_name = model or settings.gemini_model
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is required. Set it in .env file.")
        
        self.client = genai.Client(api_key=self.api_key)
    
    def extract(
        self,
        title: str,
        company: str,
        location: str,
        description_text: str,
        posted_date: str | None = None,
    ) -> tuple[ExtractedInternshipData | None, dict[str, Any]]:
        """
        Extract structured data from a job listing.
        
        Returns:
            tuple of (extracted_data, metadata)
            metadata includes: model_used, token_count, raw_response
        """
        user_prompt = build_user_prompt(
            title=title,
            company=company,
            location=location,
            description_text=description_text,
            posted_date=posted_date,
        )
        
        metadata = {
            "model_used": self.model_name,
            "token_count": None,
            "error": None,
        }
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    response_mime_type="application/json",
                    response_schema=ExtractedInternshipData,
                    temperature=0.1,  # Low temperature for consistent extraction
                    max_output_tokens=2048,
                ),
            )
            
            # Extract token usage
            if response.usage_metadata:
                metadata["token_count"] = (
                    (response.usage_metadata.prompt_token_count or 0)
                    + (response.usage_metadata.candidates_token_count or 0)
                )
            
            # Parse response
            if not response.text:
                logger.warning("Empty response from LLM")
                metadata["error"] = "Empty LLM response"
                return None, metadata
            
            # Parse JSON and validate with Pydantic
            raw_data = json.loads(response.text)
            extracted = ExtractedInternshipData.model_validate(raw_data)
            
            logger.info(
                f"Extracted data for '{title}' at '{company}' "
                f"(confidence={extracted.extraction_confidence:.2f}, "
                f"tokens={metadata['token_count']})"
            )
            
            return extracted, metadata
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON response: {e}")
            metadata["error"] = f"JSON parse error: {e}"
            return None, metadata
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            metadata["error"] = str(e)
            return None, metadata
    
    def extract_with_retry(
        self,
        title: str,
        company: str,
        location: str,
        description_text: str,
        posted_date: str | None = None,
        max_retries: int = 2,
    ) -> tuple[ExtractedInternshipData | None, dict[str, Any]]:
        """Extract with retry logic for transient failures."""
        last_metadata = {}
        
        for attempt in range(max_retries + 1):
            result, metadata = self.extract(
                title=title,
                company=company,
                location=location,
                description_text=description_text,
                posted_date=posted_date,
            )
            last_metadata = metadata
            
            if result is not None:
                return result, metadata
            
            if attempt < max_retries:
                logger.info(f"Retrying extraction (attempt {attempt + 2}/{max_retries + 1})")
        
        logger.error(f"All {max_retries + 1} extraction attempts failed for '{title}'")
        return None, last_metadata
