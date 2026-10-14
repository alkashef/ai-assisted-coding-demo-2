"""Headless-browser tests for the frozen header and the file-name lines (DEC-019)."""

from playwright.sync_api import Locator, Page, expect


def _box(locator: Locator) -> dict[str, float]:
    box = locator.bounding_box()
    assert box is not None
    return box


def _font_size(locator: Locator) -> float:
    return float(locator.evaluate("element => parseFloat(getComputedStyle(element).fontSize)"))


def _color(locator: Locator) -> str:
    return str(locator.evaluate("element => getComputedStyle(element).color"))


def _muted_color(page: Page) -> str:
    return str(
        page.evaluate(
            """() => {
                const probe = document.createElement("span");
                probe.style.color = "var(--color-muted)";
                document.body.append(probe);
                const color = getComputedStyle(probe).color;
                probe.remove();
                return color;
            }"""
        )
    )


def _assert_second_line(page: Page, name: Locator, file_name: Locator, text: str) -> None:
    expect(file_name).to_have_text(text)
    assert _box(file_name)["y"] >= _box(name)["y"] + _box(name)["height"] - 1
    assert _font_size(file_name) < _font_size(name)
    assert _color(file_name) == _muted_color(page)


def test_dec_019_ui_header_stays_at_the_top_when_the_page_scrolls(
    page: Page, ranked_base_url: str
) -> None:
    page.set_viewport_size({"width": 1000, "height": 400})
    page.goto(f"{ranked_base_url}/#/candidates/a.txt")
    expect(page.locator(".page-head-title")).to_be_visible()
    header = page.locator(".app-header")

    page.mouse.wheel(0, 3000)
    page.wait_for_function("window.scrollY > 0")

    assert _box(header)["y"] == 0


def test_dec_019_ui_navigation_file_name_is_below_the_label_in_small_grey_text(
    page: Page, ranked_base_url: str
) -> None:
    page.goto(ranked_base_url)
    link = page.locator("[data-list='candidates'] .nav-link").first
    expect(link).to_be_visible()

    _assert_second_line(page, link.locator(".nav-label"), link.locator(".nav-id"), "a.txt")


def test_dec_019_ui_card_file_name_is_below_the_name(page: Page, ranked_base_url: str) -> None:
    page.goto(f"{ranked_base_url}/#/jobs/j1.txt")
    card = page.locator(".card").first
    expect(card).to_be_visible()

    _assert_second_line(page, card.locator(".card-name"), card.locator(".card-file"), "a.txt")
    expect(card.locator(".card-sub")).to_have_text("Senior Data Analyst. Boston, United States")


def test_dec_019_ui_job_and_candidate_headings_show_the_file_name_below_the_title(
    page: Page, ranked_base_url: str
) -> None:
    page.goto(f"{ranked_base_url}/#/jobs/j1.txt")
    title = page.locator(".page-head-title")
    expect(title).to_have_text("Data Analyst")
    _assert_second_line(page, title, page.locator(".page-head-file"), "j1.txt")
    expect(page.locator(".page-head-meta")).to_have_text("All 3 candidates, best match first.")

    page.goto(f"{ranked_base_url}/#/candidates/a.txt")
    expect(title).to_have_text("Ada Invented")
    _assert_second_line(page, title, page.locator(".page-head-file"), "a.txt")
    expect(page.locator(".page-head-meta")).to_have_text("Senior Data Analyst")
