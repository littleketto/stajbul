"""Text cleaning utilities for preparing job descriptions for LLM processing."""

import re
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class TextCleaner:
    """Cleans and normalizes HTML job descriptions for LLM input."""
    
    # Maximum character count to send to LLM (token efficiency)
    MAX_TEXT_LENGTH = 4000
    
    @staticmethod
    def html_to_text(html: str) -> str:
        """Convert HTML to clean plaintext, preserving structure."""
        if not html:
            return ""
        
        soup = BeautifulSoup(html, "lxml")
        
        # Remove script and style tags
        for tag in soup.find_all(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        
        # Convert lists to readable format
        for ul in soup.find_all(["ul", "ol"]):
            for li in ul.find_all("li"):
                li.insert_before("\n• ")
        
        # Get text with newline separators
        text = soup.get_text(separator="\n", strip=True)
        return text
    
    @classmethod
    def clean(cls, text: str) -> str:
        """Full cleaning pipeline: normalize whitespace, remove noise, truncate."""
        if not text:
            return ""
        
        # Normalize unicode
        text = cls._normalize_unicode(text)
        
        # Remove excessive whitespace
        text = cls._normalize_whitespace(text)
        
        # Remove common boilerplate patterns
        text = cls._remove_boilerplate(text)
        
        # Truncate to max length
        if len(text) > cls.MAX_TEXT_LENGTH:
            text = text[:cls.MAX_TEXT_LENGTH] + "\n[...metin kesildi...]"
        
        return text.strip()
    
    @staticmethod
    def _normalize_unicode(text: str) -> str:
        """Normalize unicode characters."""
        import unicodedata
        return unicodedata.normalize("NFKC", text)
    
    @staticmethod
    def _normalize_whitespace(text: str) -> str:
        """Collapse multiple blank lines and spaces."""
        # Replace multiple spaces with single space
        text = re.sub(r'[^\S\n]+', ' ', text)
        # Replace 3+ newlines with 2
        text = re.sub(r'\n{3,}', '\n\n', text)
        # Strip each line
        lines = [line.strip() for line in text.split('\n')]
        return '\n'.join(lines)
    
    @staticmethod
    def _remove_boilerplate(text: str) -> str:
        """Remove common boilerplate text from LinkedIn job descriptions."""
        boilerplate_patterns = [
            r'(?i)show\s*more\s*/?\s*show\s*less',
            r'(?i)about\s+the\s+company',
            r'(?i)equal\s+opportunity\s+employer.*$',
            r'(?i)we\s+are\s+an\s+equal\s+opportunity.*$',
            r'(?i)linkedin\.com/.*',
            r'(?i)click\s+here\s+to\s+apply.*',
            r'(?i)for\s+more\s+information.*visit.*',
        ]
        for pattern in boilerplate_patterns:
            text = re.sub(pattern, '', text, flags=re.MULTILINE)
        return text
    
    @classmethod
    def prepare_for_llm(cls, html: str | None, plain_text: str | None) -> str:
        """Prepare job description for LLM: prefer HTML conversion, fall back to plain text."""
        if html:
            text = cls.html_to_text(html)
        elif plain_text:
            text = plain_text
        else:
            return ""
        return cls.clean(text)
