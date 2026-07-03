import os
import json
import bs4
import yaml

def load_corpus_config(config_path="config/corpus.yaml"):
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def clean_value(val):
    if val is None:
        return "N/A"
    return val

def parse_html_to_sections(raw_path, slug):
    with open(raw_path, "r", encoding="utf-8") as f:
        html = f.read()
        
    soup = bs4.BeautifulSoup(html, "html.parser")
    next_data = soup.find("script", id="__NEXT_DATA__")
    if not next_data:
        raise ValueError(f"No __NEXT_DATA__ script found in {raw_path}")
        
    data = json.loads(next_data.text)
    mf_data = data.get("props", {}).get("pageProps", {}).get("mfServerSideData", {})
    if not mf_data:
        raise ValueError(f"No mfServerSideData found in JSON props for {slug}")
        
    scheme_name = clean_value(mf_data.get("scheme_name"))
    nav = clean_value(mf_data.get("nav"))
    nav_date = clean_value(mf_data.get("nav_date"))
    expense_ratio = clean_value(mf_data.get("expense_ratio"))
    exit_load = clean_value(mf_data.get("exit_load"))
    min_investment_amount = clean_value(mf_data.get("min_investment_amount"))
    min_sip_investment = clean_value(mf_data.get("min_sip_investment"))
    benchmark_name = clean_value(mf_data.get("benchmark_name"))
    nfo_risk = clean_value(mf_data.get("nfo_risk"))
    amc_name = clean_value(mf_data.get("amc", {}).get("name") if isinstance(mf_data.get("amc"), dict) else mf_data.get("amc"))
    category = clean_value(mf_data.get("category"))
    sub_category = clean_value(mf_data.get("sub_category"))
    aum = mf_data.get("aum")
    aum_str = f"Rs. {aum:,.2f} Cr." if isinstance(aum, (int, float)) else "N/A"
    description = clean_value(mf_data.get("description"))
    
    # Extract managers
    managers_raw = mf_data.get("fund_manager_details", [])
    managers = []
    for m in managers_raw:
        m_name = clean_value(m.get("person_name"))
        m_edu = clean_value(m.get("education"))
        m_exp = clean_value(m.get("experience"))
        if m_name != "N/A":
            managers.append({
                "name": m_name,
                "bio": f"The fund is managed by {m_name}. Education: {m_edu}. Professional experience: {m_exp}."
            })
            
    sections = {
        "overview": f"The {scheme_name} is an open-ended mutual fund scheme offered by {amc_name}. Category: {category} - {sub_category}. The Net Asset Value (NAV) of the fund is Rs. {nav} as of {nav_date}. The Asset Under Management (AUM) is {aum_str}.",
        "expense_ratio": f"The expense ratio of {scheme_name} is {expense_ratio}%. The expense ratio represents the annual fee charged by the fund management house to cover administrative, management, and operational costs.",
        "exit_load": f"The exit load of {scheme_name} is: {exit_load}.",
        "minimum_investment": f"The minimum investment requirements for {scheme_name} are: Minimum lumpsum investment of Rs. {min_investment_amount}, and minimum monthly Systematic Investment Plan (SIP) investment of Rs. {min_sip_investment}.",
        "benchmark": f"The benchmark index for {scheme_name} is the {benchmark_name}.",
        "riskometer": f"The risk level (riskometer rating) of {scheme_name} is: {nfo_risk}.",
        "investment_objective": f"The investment objective of the fund is: {description}",
        "fund_management": managers
    }
    
    return sections

def parse_all(raw_dir="data/raw", processed_dir="data/processed"):
    config = load_corpus_config()
    schemes = config.get("schemes", [])
    
    for scheme in schemes:
        slug = scheme["slug"]
        if slug == "groww-platform":
            print(f"Skipping parse for static platform entry: {slug}")
            continue
            
        raw_path = os.path.join(raw_dir, f"{slug}.html")
        
        if not os.path.exists(raw_path):
            print(f"Raw HTML file not found for {slug} at {raw_path}")
            continue
            
        print(f"Parsing raw HTML for {slug}...")
        try:
            sections = parse_html_to_sections(raw_path, slug)
            
            slug_dir = os.path.join(processed_dir, slug)
            os.makedirs(slug_dir, exist_ok=True)
            sections_path = os.path.join(slug_dir, "sections.json")
            
            with open(sections_path, "w", encoding="utf-8") as f:
                json.dump(sections, f, indent=2)
                
            print(f"Successfully saved parsed sections to {sections_path}")
        except Exception as e:
            print(f"Error parsing {slug}: {e}")

if __name__ == "__main__":
    parse_all()
