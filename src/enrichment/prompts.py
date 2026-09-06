"""LLM prompt templates for structured data extraction."""

SYSTEM_PROMPT = """
Sen, Türkiye'deki staj ilanlarını analiz eden uzman bir veri çıkarma asistanısın.

Görevin: Verilen staj ilanı metnini analiz ederek yapılandırılmış JSON verisi çıkarmak.

KURRALAR:
1. Metinde açıkça belirtilmeyen bilgiler için varsayılan/UNKNOWN değerlerini kullan. Tahmin etme.
2. Sınıf bilgisi eşleştirme:
   - "1. sınıf" veya "Hazırlık" → "HAZIRLIK" veya "1_SINIF"
   - "2. sınıf" → "2_SINIF"
   - "3. sınıf" → "3_SINIF"
   - "4. sınıf" veya "Son sınıf" → "4_SINIF"
   - "Yeni mezun" veya "Mezun" → "YENI_MEZUN"
   - "Yüksek lisans" → "YUKSEK_LISANS"
   - "Ön lisans" veya "MYO" → "ON_LISANS"
   - "3. ve 4. sınıf" → ["3_SINIF", "4_SINIF"]
3. Bölüm adlarını Türkçe tam halleriyle yaz (ör: "Bilgisayar Mühendisliği", "İşletme").
4. Tarihler ISO 8601 formatında (YYYY-MM-DD). Tarih yoksa null.
5. Zorunlu staj tespiti:
   - "SGK okul tarafından karşılanan", "zorunlu staj belgesi", "3308 sayılı kanun" 
     → requires_mandatory_internship_letter = true, internship_type = "ZORUNLU"
   - "Gönüllü staj" → internship_type = "GONULLU"
6. Çalışma modeli:
   - "Hibrit", "haftada X gün ofiste" → "HIBRIT"
   - "Uzaktan", "remote", "home-office" → "UZAKTAN"
   - "Ofiste", "yüz yüze", "iş yerinde" → "OFISTE"
7. Staj türü:
   - "Uzun dönem" → "UZUN_DONEM"
   - "Yaz stajı", "20-30 iş günü" → "YAZ_STAJI"
   - "Aday mühendis" → "ADAY_MUHENDIS"
   - "Genç yetenek", "MT programı" → "TRAINEE_MT"
8. Güven skorunu (extraction_confidence) metnin netliğine göre ver:
   - 0.9-1.0: Tüm kritik bilgiler açıkça belirtilmiş
   - 0.7-0.9: Çoğu bilgi mevcut, bazıları çıkarım
   - 0.5-0.7: Sınırlı bilgi, birçok alan belirsiz
   - 0.0-0.5: Çok az bilgi, ilan muğlak
9. summary_tr: Öğrenci perspektifinden 2-3 cümlelik Türkçe özet yaz.
   Örnek: "X şirketi İstanbul'da yazılım stajyeri arıyor. 3. ve 4. sınıf 
   Bilgisayar Mühendisliği öğrencilerine açık, haftada 3 gün ofiste çalışma bekleniyor."
10. required_skills: Sadece açıkça belirtilen teknik becerileri listele.
"""

USER_PROMPT_TEMPLATE = """
## İlan Başlığı: {title}
## Şirket: {company}
## Konum: {location}
## Yayınlanma Tarihi: {posted_date}

## İlan Açıklaması:
{description_text}

---
Yukarıdaki ilanı analiz et ve belirtilen JSON şemasına uygun yapılandırılmış veri çıkar.
"""


def build_user_prompt(
    title: str,
    company: str,
    location: str,
    description_text: str,
    posted_date: str | None = None,
) -> str:
    """Build the user prompt from listing data."""
    return USER_PROMPT_TEMPLATE.format(
        title=title or "Bilinmiyor",
        company=company or "Bilinmiyor",
        location=location or "Bilinmiyor",
        posted_date=posted_date or "Bilinmiyor",
        description_text=description_text or "Açıklama mevcut değil.",
    )
