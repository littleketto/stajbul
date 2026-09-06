"""Post-LLM validation and normalization of extracted data."""

import json
import logging
from pathlib import Path

from src.models.schemas import ExtractedInternshipData
from src.models.enums import DepartmentCategory

logger = logging.getLogger(__name__)


class DataValidator:
    """Validates and normalizes LLM-extracted internship data."""
    
    def __init__(self):
        self._department_map: dict[str, str] = {}  # alias -> canonical name
        self._department_categories: dict[str, str] = {}  # name -> category
        self._valid_cities: set[str] = set()
        self._load_reference_data()
    
    def _load_reference_data(self):
        """Load reference data for validation."""
        data_dir = Path(__file__).resolve().parent.parent.parent / "data"
        
        # Load departments
        dept_file = data_dir / "departments.json"
        if dept_file.exists():
            with open(dept_file, "r", encoding="utf-8") as f:
                departments = json.load(f)
            for dept in departments:
                canonical = dept["name_tr"]
                self._department_categories[canonical.lower()] = dept["category"]
                self._department_map[canonical.lower()] = canonical
                for alias in dept.get("aliases", []):
                    self._department_map[alias.lower()] = canonical
                if dept.get("name_en"):
                    self._department_map[dept["name_en"].lower()] = canonical
        
        # Load cities
        cities_file = data_dir / "cities.json"
        if cities_file.exists():
            with open(cities_file, "r", encoding="utf-8") as f:
                cities = json.load(f)
            for city in cities:
                self._valid_cities.add(city["name"])
    
    def validate_and_normalize(
        self, data: ExtractedInternshipData
    ) -> ExtractedInternshipData:
        """Validate and normalize extracted data."""
        # Normalize department names
        data.eligible_departments = self._normalize_departments(data.eligible_departments)
        
        # Ensure department_categories match eligible_departments
        if data.eligible_departments and not data.department_categories:
            data.department_categories = self._infer_categories(data.eligible_departments)
        
        # Normalize city name
        if data.city:
            data.city = self._normalize_city(data.city)
        
        # Validate date consistency
        data = self._validate_dates(data)
        
        # Clamp confidence score
        data.extraction_confidence = max(0.0, min(1.0, data.extraction_confidence))
        
        return data
    
    def _normalize_departments(self, departments: list[str]) -> list[str]:
        """Normalize department names to canonical Turkish forms."""
        normalized = []
        for dept in departments:
            canonical = self._department_map.get(dept.lower())
            if canonical:
                if canonical not in normalized:
                    normalized.append(canonical)
            else:
                # Keep original if no match found
                if dept not in normalized:
                    normalized.append(dept)
                logger.debug(f"Unknown department: '{dept}'")
        return normalized
    
    def _infer_categories(
        self, departments: list[str]
    ) -> list[DepartmentCategory]:
        """Infer department categories from department names."""
        categories = set()
        for dept in departments:
            cat = self._department_categories.get(dept.lower())
            if cat:
                try:
                    categories.add(DepartmentCategory(cat))
                except ValueError:
                    pass
        return list(categories)
    
    def _normalize_city(self, city: str) -> str:
        """Normalize city name to match reference data."""
        # Direct match
        if city in self._valid_cities:
            return city
        
        # Case-insensitive match
        for valid_city in self._valid_cities:
            if city.lower() == valid_city.lower():
                return valid_city
        
        # Common aliases
        city_aliases = {
            "istanbul": "İstanbul",
            "İstanbul": "İstanbul",
            "ankara": "Ankara",
            "izmir": "İzmir",
            "İzmir": "İzmir",
            "bursa": "Bursa",
            "kocaeli": "Kocaeli",
            "gebze": "Kocaeli",
            "antalya": "Antalya",
            "eskisehir": "Eskişehir",
            "eskişehir": "Eskişehir",
        }
        normalized = city_aliases.get(city.lower())
        if normalized:
            return normalized
        
        # Return as-is if no match
        return city
    
    def _validate_dates(self, data: ExtractedInternshipData) -> ExtractedInternshipData:
        """Validate date consistency."""
        # Ensure start_date is before end_date
        if data.start_date and data.end_date and data.start_date > data.end_date:
            logger.warning(
                f"start_date ({data.start_date}) is after end_date ({data.end_date}). Swapping."
            )
            data.start_date, data.end_date = data.end_date, data.start_date
        
        return data
