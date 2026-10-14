"""Headless-browser tests for the candidate view: raw CV, attributes and ranked job descriptions."""

from playwright.sync_api import Page, expect


def _open_candidate(page: Page, base_url: str, candidate_id: str = "a.txt") -> None:
    page.goto(f"{base_url}/#/candidates/{candidate_id}")
    expect(page.locator(".page-head-title")).to_be_visible()


def test_cnd_001_ui_selecting_a_candidate_shows_the_raw_cv(
    page: Page, ranked_base_url: str
) -> None:
    page.goto(ranked_base_url)
    page.locator("[data-list='candidates'] .nav-link").first.click()

    expect(page.get_by_role("heading", name="Ada Invented", level=2)).to_be_visible()
    expect(page.locator(".doc-text")).to_have_text("Cv A")
    expect(page.locator("[data-empty]")).to_be_hidden()


def test_cnd_002_ui_shows_extracted_and_calculated_attributes(
    page: Page, ranked_base_url: str
) -> None:
    _open_candidate(page, ranked_base_url)

    expect(page.locator(".page-head-meta")).to_have_text("Senior Data Analyst")
    labels = page.locator(".facts-label")
    expect(labels).to_have_text(
        [
            "Current job title",
            "Current address",
            "Highest degree",
            "Skills",
            "Countries worked in",
            "Companies",
            "Last job",
            "Total employment",
            "Jobs held",
            "Average per job",
            "Employment gaps",
            "Since graduation",
            "Currently employed",
        ]
    )
    values = page.locator(".facts-value")
    expect(values.nth(0)).to_have_text("Senior Data Analyst")
    expect(values.nth(1)).to_have_text("Boston, United States")
    expect(page.locator(".chips-item")).to_have_text(["SQL", "Tableau"])
    expect(values.nth(6)).to_contain_text("Senior Data Analyst at Northwind Invented")
    expect(values.nth(7)).to_have_text("106 months")
    expect(values.nth(8)).to_have_text("3")
    expect(values.nth(9)).to_have_text("35.3 months")
    expect(values.nth(10)).to_have_text("1 gap: 5 months")
    expect(values.nth(11)).to_have_text("102 months")
    expect(values.nth(12)).to_have_text("Yes")


def test_cnd_003_ui_shows_the_job_descriptions_ranked_with_scores(
    page: Page, ranked_base_url: str
) -> None:
    _open_candidate(page, ranked_base_url)

    items = page.locator(".ranking-item")
    expect(items).to_have_count(1)
    expect(items.first.locator(".ranking-rank")).to_have_text("1")
    expect(items.first.locator(".ranking-title")).to_have_text("Data Analyst")
    expect(items.first.locator(".ranking-title")).to_have_attribute("href", "#/jobs/j1.txt")
    expect(items.first.locator(".ranking-score")).to_have_text("0.71")
    expect(page.locator(".badge")).to_have_count(0)


def test_mis_001_ui_missing_attribute_shows_not_available(page: Page, ranked_base_url: str) -> None:
    _open_candidate(page, ranked_base_url, "c.txt")

    expect(page.locator(".page-head-title")).to_have_text("Not available")
    expect(page.locator(".facts-value").first).to_have_text("Not available")
    expect(page.locator(".facts-value").first).to_have_class("facts-value not-available")
    expect(page.locator(".facts-value").nth(7)).to_have_text("Not available")
    expect(page.locator(".ranking-item")).to_have_count(0)


def test_cnd_001_ui_unknown_candidate_shows_the_not_found_panel(
    page: Page, ranked_base_url: str
) -> None:
    page.goto(f"{ranked_base_url}/#/candidates/9999.txt")

    expect(page.get_by_role("heading", name="Candidate not found")).to_be_visible()
    expect(page.locator("[data-field=text]")).to_contain_text("No candidate with ID 9999.txt")
