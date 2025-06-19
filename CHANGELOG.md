
## Changelog

### Unreleased
- Added `static/js/ui.js` for scroll observers, navbar transparency, and theme helpers. Base template now loads this file and no longer includes inline scripts.
- Added performance sections dropdown in navbar and removed inline dropdown blocks from policy pages.
- Configured Tailwind build with DaisyUI plugin and new `input.css`; mobile menu now transitions smoothly and navbar padding defaults to `py-6` for initial tests.
- Bundled Alpine.js locally under `static/js` and updated templates to load it instead of the CDN script.
- Replaced Tailwind and DaisyUI CDN links with a local build using `npx tailwindcss`; Netlify now compiles `static/styles.css`.
- Fixed Netlify build by installing Tailwind CLI via npm and running `npm ci` before compilation.
- Created `REVAMP` branch from `work` to continue UI/UX revamp tasks.
- Added responsive DaisyUI navbar with Tailwind and Alpine.js; active page now highlighted via context.
- Cleaned up `README.md` by removing shell prompt artifacts and adding missing license closing text.
- Added pytest fixture that freezes the site if `build/index.html` is missing; documented this under "Running Tests".
- Added pytest-based tests for key routes and documented how to run them.
- Added Netlify deployment files and documentation.
- Integrated performance policy visuals from `NEW_Images` with fade-in transitions and alternating layout.
- Switched navbar opacity logic to an IntersectionObserver watching `#top-sentinel` and removed the body scroll handler.
- Fixed incorrect asset paths and gave images rounded corners; added tests ensuring `NEW_Images` load correctly.
- Added phase navigation buttons on the performance index and fade-out transitions for scrollable sections.
- Fixed trailing prompt artifact in `test.py`.
- Integrated performance policy pages and routes.
- Fixed Netlify configuration parse error by using `python_version` in `netlify.toml`.
- Removed fixed header/nav offsets; navbar now uses `sticky top-0` and body padding was dropped in favor of Tailwind spacing.
- Updated Netlify configuration to remove unsupported `python_version` property.
- Fixed functions directory path so Netlify deploy detects Python functions.
- Added base path stripping and included files to ensure Flask routes work on Netlify.
- Made Flask server port configurable via `PORT` env variable and updated Dockerfile.
- Read serverless function base path from `API_GATEWAY_BASE_PATH` environment
  variable and documented the setting in Netlify configuration.
- Replaced Python 3.10 union type hints with `typing.Optional` for
  compatibility with Netlify's Python runtime.
- Updated Netlify redirect to include `:splat` so route paths reach the Flask
  function correctly.
- Added Alpine.js theme state and navbar toggle; preferences persist via `localStorage`.
- Set `publish = "templates"` in Netlify configuration so deploys upload the site's HTML files.
- Switched Netlify deploy to Frozen-Flask static build with `freeze.py` and new workflow.
- Fixed failing route tests by adjusting `tests/test_routes.py` to load the
  local module explicitly.
- Added new unit tests covering the `/models` API and performance policy pages.
- Replaced legacy performance policy with new policy structure and HTML sections.
- Ensured Frozen-Flask outputs `.html` files for performance policy subpages.
- Switched page logo to backgroundless variant.
- Added dropdown navigation and arrow-style back buttons on performance policy pages.
- Embedded policy explanation video at the top of the performance index page.
- Fixed integration policy page by serving it at `/politique/` and redirecting the legacy path.
- Added direct section links at the bottom of the performance index page and ensured dropdowns toggle via JavaScript.
- Expanded route tests to cover all pages and updated politique path tests.
- Added circular stage buttons on the performance index page with links to each phase and new route tests.
- Added unit tests for Ollama query logic and fallback handling.
- Fixed duplicate Docker build/run commands in README.
- Implemented basic internationalization with i18next, French/English locale files, and a navbar language switcher.
- Reworked layout using Tailwind sections and DaisyUI cards; removed redundant CSS and improved image alt text.
- Integrated Tippy.js tooltips for glossary terms (dopamine, probiotiques, freemium, NurrIA) with theme-aware initialization and i18n support. Added tooltip translations in locale files.
- Animated header fades out on scroll and mobile menu now transitions smoothly.
- Navbar now shrinks on scroll and logo slides to the left for a cleaner sticky header.
- Logo now physically moves from the header into the navbar on scroll, and menu buttons use consistent DaisyUI styles with a working dark-mode toggle.
- Replaced custom section and footer CSS with DaisyUI classes; unified heading styles across templates and removed unused rules.
- Theme initialization moved to `ui.js` with inline fallback script; toggle button now updates `aria-pressed` and persists selection.
- Improved spacing for navbar buttons and grouped theme toggle with language switcher.
- Fixed dark/light toggle regression and polished menu styles with rounded borders and hover highlights.
- Spaced out menu buttons further with hover scaling; theme toggle icons display side-by-side above language switcher and brand text hides on scroll.
- Replaced checkbox theme switch with an accessible button that toggles `aria-pressed` and swaps sun/moon icons without layout shift.
- Fixed static build producing extensionless pages; patched freezer to write `index.html` files and added tests checking for markdown.
- Replaced custom section and footer CSS with DaisyUI classes; unified heading styles across templates and removed unused rules.

## [Unreleased]
- Converted test.py to unittest and removed stray prompt text.
- Added `.gitignore` to exclude Python artifacts and environment files.
- Removed committed `__pycache__/` directory from version control.

- Added Playwright integration tests and updated CI to run them in headed mode.
