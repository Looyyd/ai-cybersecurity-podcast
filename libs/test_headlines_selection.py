from .headlines_selection import select_headlines

def test_select_headlines_return_type():
    n_headline = 3
    days = 3

    result = select_headlines(n_headline, days)

    assert isinstance(result, list), "The result should be a list"

def test_select_headlines_list_length():
    n_headline = 3
    days = 3

    result = select_headlines(n_headline, days)

    assert len(result) == n_headline, f"The result should have {n_headline} items"

def test_select_headlines_list_items_structure():
    n_headline = 3
    days = 3

    result = select_headlines(n_headline, days)

    for item in result:
        assert isinstance(item, dict), "Each item in the result should be a dictionary"
        assert "title" in item, "Each item should have a 'title' key"
        assert "links" in item, "Each item should have a 'links' key"
        assert isinstance(item["title"], str), "The 'title' should be a string"
        assert isinstance(item["links"], list), "The 'links' should be a list"

def test_select_headlines_max_links():
    n_headline = 3
    days = 3
    max_links = 3

    result = select_headlines(n_headline, days)

    for item in result:
        assert len(item["links"]) <= max_links, f"There should be no more than {max_links} links per item"

