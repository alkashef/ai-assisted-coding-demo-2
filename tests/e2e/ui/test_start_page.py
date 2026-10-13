"""Headless-browser tests for the start page: the lists and the failure notice."""

from playwright.sync_api import Page, expect


def test_dec_002_ui_page_loads_without_script_errors(
    page: Page, base_url: str, script_errors: list[str]
) -> None:
    page.goto(base_url)
    expect(page.locator("[data-list='jobs'] .nav-link")).to_have_count(2)

    assert script_errors == []


def test_lst_001_ui_lists_the_job_descriptions(page: Page, base_url: str) -> None:
    page.goto(base_url)

    links = page.locator("[data-list='jobs'] .nav-link")
    expect(links).to_have_count(2)
    expect(links.nth(0)).to_contain_text("Data Analyst")
    expect(links.nth(0)).to_contain_text("j1.txt")
    expect(links.nth(1)).to_contain_text("Site Engineer")
    expect(links.nth(1)).to_have_attribute("href", "#/jobs/j2.txt")
    expect(page.get_by_role("heading", name="Job descriptions (2)")).to_be_visible()


def test_lst_002_ui_lists_the_candidates(page: Page, base_url: str) -> None:
    page.goto(base_url)

    links = page.locator("[data-list='candidates'] .nav-link")
    expect(links).to_have_count(3)
    expect(links.nth(0)).to_contain_text("Ada Invented")
    expect(links.nth(0)).to_contain_text("a.txt")
    expect(links.nth(2)).to_contain_text("Bo Invented")
    expect(links.nth(2)).to_have_attribute("href", "#/candidates/c.txt")
    expect(page.get_by_role("heading", name="Candidates (3)")).to_be_visible()


def test_err_001_ui_shows_the_failure_notice_with_the_causes(page: Page, base_url: str) -> None:
    page.goto(base_url)

    notice = page.get_by_role("status")
    expect(notice).to_contain_text("2 results could not be computed")
    items = notice.locator("li")
    expect(items).to_have_count(2)
    expect(items.nth(0)).to_have_text("b.txt: Extraction failed: rate limited")
    expect(items.nth(1)).to_have_text("j1.txt + c.txt: Recommendation failed: timed out")


def test_mis_001_ui_shows_not_available_for_a_missing_candidate_name(
    page: Page, base_url: str
) -> None:
    page.goto(base_url)

    missing_name = page.locator("[data-list='candidates'] .nav-link").nth(1).locator(".nav-label")
    expect(missing_name).to_have_text("Not available")
    expect(missing_name).to_have_class("nav-label not-available")
