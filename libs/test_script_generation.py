import pytest
from .text_generation import create_headlines_to_podcast_prompt, headlines_to_podcast_script_gpt4

@pytest.fixture
def selected_headlines():
    return [
        {"title": "Hackers target vulnerable Veeam backup servers exposed online", "links": ["https://www.bleepingcomputer.com/news/security/hackers-target-vulnerable-veeam-backup-servers-exposed-online/"]},
        {"title": "Coercion in the Age of Ransomware: New Tactics for Extorting Payments", "links": ["https://cyware.com/news/coercion-in-the-age-of-ransomware-new-tactics-for-extorting-payments-0c31dba6/?&web_view=true"]},
        {"title": "Atomic macOS Malware Steals Auto-fills, Passwords, Cookies, Wallets", "links": ["https://cybersecuritynews.com/atomic-macos-malware/"]},
        {"title": "Top 13 SaaS Cybersecurity Threats in 2023: Is Your Business Prepared?", "links": ["https://cybersecuritynews.com/saas-cybersecurity-threats/"]}
    ]

def test_create_headlines_to_podcast_prompt(selected_headlines):
    podcast_number = 1
    result = create_headlines_to_podcast_prompt(selected_headlines, podcast_number)
    assert isinstance(result, str)
    assert len(result) > 0

def test_headlines_to_podcast_script_gpt4(selected_headlines):
    podcast_number = 1
    result = headlines_to_podcast_script_gpt4(selected_headlines, podcast_number)
    assert isinstance(result, str)
    assert len(result) > 0
