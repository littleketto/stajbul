"""Seed the departments table from the reference JSON file."""

import json
from pathlib import Path

from src.storage.engine import get_engine, init_db, get_db_session
from src.storage.repositories import DepartmentRepository


def seed_departments():
    """Load departments from data/departments.json into the database."""
    data_file = Path(__file__).resolve().parent.parent / "data" / "departments.json"
    
    if not data_file.exists():
        print(f"Error: {data_file} not found.")
        return
    
    with open(data_file, "r", encoding="utf-8") as f:
        departments = json.load(f)
    
    engine = get_engine()
    init_db(engine)  # Ensure tables exist
    
    with get_db_session(engine) as session:
        repo = DepartmentRepository(session)
        created = 0
        updated = 0
        
        for dept_data in departments:
            dept = repo.upsert(
                name_tr=dept_data["name_tr"],
                name_en=dept_data.get("name_en"),
                category=dept_data["category"],
                aliases=dept_data.get("aliases", []),
            )
            if dept.id is None:
                created += 1
            else:
                updated += 1
        
        print(f"Seeded {len(departments)} departments ({created} new, {updated} updated).")


if __name__ == "__main__":
    seed_departments()
