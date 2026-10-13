"""Headless-browser test for the stale-response guard: an ID is unique only within its kind."""

from playwright.sync_api import Page, Route, expect

_HOLD_POLL_MS = 50
_HOLD_POLL_LIMIT = 200


def _hold_job_request(page: Page) -> list[Route]:
    """Holds the ranked-candidates request of the job and returns the list that collects it."""
    held: list[Route] = []

    def hold(route: Route) -> None:
        held.append(route)

    page.route("**/api/jobs/same.txt/ranked-candidates", hold)
    return held


def _wait_until_held(page: Page, held: list[Route]) -> None:
    for _ in range(_HOLD_POLL_LIMIT):
        if held:
            return
        page.wait_for_timeout(_HOLD_POLL_MS)
    raise AssertionError("The job request was never held")


def test_jobs_and_candidates_ui_late_response_does_not_replace_the_current_view(
    page: Page, shared_id_base_url: str
) -> None:
    held = _hold_job_request(page)
    page.goto(shared_id_base_url)
    page.locator("[data-list='jobs'] .nav-link").click()
    _wait_until_held(page, held)

    page.locator("[data-list='candidates'] .nav-link").click()
    heading = page.get_by_role("heading", name="Ada Invented", level=2)
    expect(heading).to_be_visible()
    held[0].continue_()
    page.wait_for_load_state("networkidle")

    expect(heading).to_be_visible()
    expect(page.locator(".card")).to_have_count(0)
