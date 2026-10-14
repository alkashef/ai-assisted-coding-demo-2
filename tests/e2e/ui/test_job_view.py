"""Headless-browser tests for the job view: the ranked candidate cards."""

from playwright.sync_api import Page, expect


def _open_job(page: Page, base_url: str) -> None:
    page.goto(f"{base_url}/#/jobs/j1.txt")
    expect(page.locator(".card")).to_have_count(3)


def test_job_002_ui_selecting_a_job_description_shows_all_candidates_best_first(
    page: Page, ranked_base_url: str
) -> None:
    page.goto(ranked_base_url)
    page.locator("[data-list='jobs'] .nav-link").first.click()

    cards = page.locator(".card")
    expect(cards).to_have_count(3)
    expect(page.get_by_role("heading", name="Data Analyst", level=2)).to_be_visible()
    expect(cards.nth(0).locator(".card-rank")).to_have_text("1")
    expect(cards.nth(0).locator(".card-name")).to_have_text("Ada Invented")
    expect(cards.nth(0).locator(".card-score-value")).to_have_text("0.71")
    expect(cards.nth(0).locator(".card-name a")).to_have_attribute("href", "#/candidates/a.txt")
    expect(cards.nth(1).locator(".card-score-value")).to_have_text("0.40")


def test_rnk_003_ui_card_shows_extracted_and_calculated_attributes(
    page: Page, ranked_base_url: str
) -> None:
    _open_job(page, ranked_base_url)

    card = page.locator(".card").first
    expect(card.locator(".card-sub")).to_have_text("Senior Data Analyst. Boston, United States")
    stats = card.locator(".stat-value")
    expect(stats).to_have_text(
        ["106 months", "3", "35.3 months", "1 gap: 5 months", "Yes", "102 months"]
    )
    expect(card.locator(".card-last-job")).to_contain_text(
        "Senior Data Analyst at Northwind Invented, Boston, United States. 2019-03 to Present."
    )
    expect(card.locator(".card-last-job")).to_contain_text("Leads reporting pipelines.")
    card.get_by_text("More attributes").click()
    expect(card.locator(".facts-value").nth(4)).to_have_text("Northwind Invented")
    expect(card.locator(".chips-item")).to_have_text(["SQL", "Tableau"])


def test_ext_009_ui_current_job_shows_present(page: Page, ranked_base_url: str) -> None:
    _open_job(page, ranked_base_url)

    expect(page.locator(".card").nth(0).locator(".card-last-job")).to_contain_text(
        "2019-03 to Present."
    )


def test_ext_009_ui_unknown_end_shows_not_available(page: Page, ranked_base_url: str) -> None:
    _open_job(page, ranked_base_url)

    last_job = page.locator(".card").nth(2).locator(".card-last-job")
    expect(last_job).to_contain_text("2015-02 to Not available.")
    expect(last_job).not_to_contain_text("Present")


def test_rec_001_ui_card_shows_the_recommendation_badge_and_reason(
    page: Page, ranked_base_url: str
) -> None:
    _open_job(page, ranked_base_url)

    cards = page.locator(".card")
    expect(cards.nth(0).locator(".badge")).to_have_text("Interview")
    expect(cards.nth(0).locator(".card-reason")).to_have_text("Strong reporting background.")
    expect(cards.nth(1).locator(".badge")).to_have_text("Do not interview")
    expect(cards.nth(1).locator(".card-reason")).to_have_text("No analytics experience.")


def test_mis_001_ui_missing_value_shows_not_available(page: Page, ranked_base_url: str) -> None:
    _open_job(page, ranked_base_url)

    card = page.locator(".card").nth(1)
    expect(card.locator(".card-name")).to_have_text("Not available")
    expect(card.locator(".stat-value").first).to_have_text("Not available")
    card.get_by_text("More attributes").click()
    missing = card.locator(".facts-value").first
    expect(missing).to_have_text("Not available")
    expect(missing).to_have_class("facts-value not-available")


def test_mis_002_ui_candidate_without_a_score_is_listed_last(
    page: Page, ranked_base_url: str
) -> None:
    _open_job(page, ranked_base_url)

    last = page.locator(".card").nth(2)
    expect(last.locator(".card-rank")).to_have_text("3")
    expect(last.locator(".card-name")).to_have_text("Bo Invented")
    expect(last.locator(".card-score-value")).to_have_text("Not available")
    expect(last.locator(".badge")).to_have_text("Not available")


def test_job_003_ui_selecting_a_job_shows_its_text_above_the_ranked_candidates(
    page: Page, ranked_base_url: str
) -> None:
    _open_job(page, ranked_base_url)

    panel = page.locator("details.doc")
    expect(panel.locator("summary")).to_have_text("Job description text")
    expect(panel.locator(".doc-text")).to_have_text("Data Analyst\nInvented details")
    panel_box = panel.bounding_box()
    card_box = page.locator(".card").first.bounding_box()
    assert panel_box is not None
    assert card_box is not None
    assert panel_box["y"] < card_box["y"]
