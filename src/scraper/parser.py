from bs4 import BeautifulSoup
from datetime import date, datetime, timedelta
import re
import logging
from src.models.schemas import ScrapedJobCard, ScrapedJobDetail

logger = logging.getLogger(__name__)

class LinkedInParser:
    """Parses LinkedIn guest job pages HTML into structured data."""
    
    @staticmethod
    def parse_search_results(html: str) -> list[ScrapedJobCard]:
        cards = []
        soup = BeautifulSoup(html, "html.parser")
        
        job_elements = soup.find_all("li")
        if not job_elements:
            job_elements = soup.find_all("div", class_="base-card")
            
        for card in job_elements:
            try:
                # URL and Job ID
                link_tag = card.find("a", class_="base-card__full-link") or card.find("a", class_="job-search-card__title")
                if not link_tag or not link_tag.get("href"):
                    continue
                url = link_tag["href"]
                job_id = LinkedInParser._extract_job_id_from_url(url)
                
                # Title
                title_tag = (
                    card.find("h3", class_="base-search-card__title")
                    or card.find("h3", class_="job-search-card__title") 
                    or card.find("h3")
                )
                title = title_tag.text.strip() if title_tag else ""
                
                # Company
                company_tag = (
                    card.find("h4", class_="base-search-card__subtitle")
                    or card.find("a", class_="hidden-nested-link")
                )
                company = company_tag.text.strip() if company_tag else ""
                
                # Location
                location_tag = card.find("span", class_="job-search-card__location")
                location = location_tag.text.strip() if location_tag else ""
                
                # Date
                time_tag = card.find("time")
                posted_date = None
                if time_tag and time_tag.get("datetime"):
                    try:
                        posted_date = datetime.strptime(time_tag["datetime"], "%Y-%m-%d").date()
                    except ValueError:
                        pass
                elif time_tag:
                    posted_date = LinkedInParser._parse_relative_date(time_tag.text.strip())
                
                if job_id and title and company:
                    cards.append(ScrapedJobCard(
                        job_id=job_id,
                        title=title,
                        company=company,
                        location=location,
                        posted_date=posted_date,
                        url=url
                    ))
            except Exception as e:
                logger.error(f"Error parsing job card: {e}")
                continue
                
        return cards
    
    @staticmethod
    def parse_job_detail(html: str, job_id: str) -> ScrapedJobDetail:
        soup = BeautifulSoup(html, "html.parser")
        
        desc_div = soup.find("div", class_="show-more-less-html__markup") or soup.find("div", class_="description__text")
        description_html = str(desc_div) if desc_div else ""
        description_text = desc_div.get_text(separator="\n", strip=True) if desc_div else ""
        
        detail = ScrapedJobDetail(
            job_id=job_id,
            description_html=description_html,
            description_text=description_text
        )
        
        criteria_list = soup.find("ul", class_="description__job-criteria-list")
        if criteria_list:
            items = criteria_list.find_all("li")
            for item in items:
                header = item.find("h3")
                value = item.find("span")
                if header and value:
                    h_text = header.text.strip().lower()
                    v_text = value.text.strip()
                    if "seniority level" in h_text:
                        detail.seniority_level = v_text
                    elif "employment type" in h_text:
                        detail.employment_type = v_text
                    elif "job function" in h_text:
                        detail.job_function = v_text
                    elif "industries" in h_text:
                        detail.industries = v_text
                        
        return detail
    
    @staticmethod
    def _extract_job_id_from_url(url: str) -> str | None:
        match = re.search(r'(\d{8,12})', url)
        return match.group(1) if match else None
    
    @staticmethod
    def _parse_relative_date(date_text: str) -> date | None:
        if not date_text:
            return None
            
        today = date.today()
        text = date_text.lower()
        
        try:
            val = int(re.search(r'\d+', text).group())
            if "minute" in text or "hour" in text:
                return today
            elif "day" in text:
                return today - timedelta(days=val)
            elif "week" in text:
                return today - timedelta(weeks=val)
            elif "month" in text:
                return today - timedelta(days=val * 30)
        except (AttributeError, ValueError):
            pass
            
        return today
