import pytest

@pytest.mark.playwright
def test_mobile_menu_toggle(adopt, server):
    page = adopt
    page.set_viewport_size({'width': 375, 'height': 640})
    page.goto(server)
    menu = page.locator('ul.menu-compact')
    assert not menu.is_visible()
    # Ensure transition classes are applied for smooth animation
    assert 'transition-all' in menu.get_attribute('class')
    page.click('button[aria-label="Toggle navigation"]')
    page.wait_for_timeout(200)
    assert menu.is_visible()
