"""Registry of authoritative sources per jurisdiction. Only URLs listed here are ever fetched (no user-supplied URLs).
Edit this registry to add jurisdictions. URLs are starting points and must be verified by a human before relying on them."""
SOURCES = {
    "IN": {"regulation": "Digital Personal Data Protection Act, 2023", "sources": [
        {"name": "MeitY - data protection framework", "url": "https://www.meity.gov.in/data-protection-framework"}]},
    "EU": {"regulation": "General Data Protection Regulation (EU) 2016/679", "sources": [
        {"name": "EUR-Lex - GDPR (CELEX 32016R0679)", "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32016R0679"}]},
    "US-CA": {"regulation": "California Consumer Privacy Act as amended by CPRA", "sources": [
        {"name": "California Privacy Protection Agency - regulations", "url": "https://cppa.ca.gov/regulations/"}]},
}
