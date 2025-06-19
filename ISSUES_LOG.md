## Issues Log

- [ ] Test script fails due to network access restrictions when reaching n8n webhook.
- [ ] Netlify deployment may fail if Ollama endpoints are blocked or require authentication.
- Added local Flask route tests using pytest to avoid network failures.
- [x] Route tests initially failed with `ModuleNotFoundError: No module named`
  `app`; fixed by prepending the project root to `sys.path` in tests.
- [ ] Performance policy pages need improved responsive styling.
- [ ] Assess accessibility of new dropdown and arrow navigation.
- [ ] Verify new policy sections render correctly after restructuring.
- [x] Performance policy subpages frozen without `.html` extension caused raw Markdown display. Patched `freeze.py` to append `.html`.
- [x] Integration policy page served as raw text because Frozen-Flask output lacked extension. Added trailing-slash route and redirect so file builds as `politique/index.html`.
- [x] Netlify deploy failed to parse configuration; replaced `python_runtime` with `python_version`.
- [x] Netlify deploy still failed due to `python_version`; removed the property entirely.
- [x] Netlify deploy preview served 404s due to functions not detected; added explicit directory setting.
- [x] Ensure Netlify build has Node.js available for the Tailwind CLI step; added npm install step and Tailwind CLI dependency.
- [x] Deployed site still returns 404; added base path stripping and included files for templates. Parameterized the base path via `API_GATEWAY_BASE_PATH` to allow configuration. Verified after switching to Frozen-Flask build.
- [x] Netlify served raw Jinja templates due to missing build step; replaced config with Frozen-Flask to generate static HTML.
- [x] Redirect did not forward the requested path to the Flask function; added `:splat` to the Netlify redirect.
- [x] Netlify deploy uploaded 0 files because no publish directory was defined. Set `publish = "templates"` in `netlify.toml` to ensure pages are uploaded.
- [x] Performance index lacked quick navigation buttons; added circular stage buttons and tests.
- [ ] Netlify Python runtime may be <3.10 causing syntax errors from union type
      hints. Updated code to use `typing.Optional` for compatibility.
- [ ] Docker container may not honor `PORT` variable due to exec-form CMD.
- Added tests for Ollama query and fallback functions to ensure reliability.
- [x] Duplicate Docker commands in README created confusion; removed extra build/run lines.
- [x] Tests failed when the `build/` directory was missing. Added an autouse fixture to generate the static site before tests.
- [ ] Verify DaisyUI navbar works consistently across browsers.
- [x] Ensure new theme toggle functions across browsers and persists across sessions.
- [x] Confirm accessible theme button sets `aria-pressed` correctly and swaps icons without causing layout shift.
- [x] Navigation menu lacked hover highlight and rounded borders; centered menu and added hover styles.
- [ ] Expand translations to remaining pages and content.
- [x] Old page-specific CSS made maintenance difficult; migrated to Tailwind utility classes and DaisyUI components.
- [ ] Verify mobile behavior of new tooltips.
- [x] Sticky header offset caused extra space; switched navbar to `top-0` and removed body padding.
- [x] Header now hides on scroll and mobile menu fades in/out for smoother navigation.
- [x] Navbar shrinks and logo moves left when scrolling down, restoring when scrolling up.
- [x] Logo now relocates between header and navbar on scroll and dark-mode toggle is functional.
- [x] Inconsistent typography across templates; applied Tailwind heading classes and DaisyUI prose sections.

- [x] `flask_frozen` dependency missing during tests; added fallback freezer to run tests offline.
- [x] Performance images returned 404 due to incorrect paths; filenames corrected and tests added.
- [ ] Some office scene images referenced in `image_placement_instructions.md` are absent from the repository.
- [x] Navbar buttons spaced evenly; toggle and language buttons aligned.
- [x] Added spacing and hover scaling to menu items; theme toggle now shows icons side by side above language buttons. Removed brand text when navbar shrinks.
- [x] Frozen-Flask wrote pages without `.html` extensions causing markdown-like display; patched freezer and added build tests.
- [x] Inconsistent typography across templates; applied Tailwind heading classes and DaisyUI prose sections.

- [x] Integrated Sections dropdown; removed duplicated dropdown blocks from policy pages.
- [x] Moved fade-section observer into `static/js/ui.js` with navbar sentinel logic; base template references the new script.
- [x] Replaced `@scroll.window` listener with custom `sentinel-change` event; navbar opacity toggles via IntersectionObserver.
- [x] Added Playwright tests for theme toggle, navbar transparency and mobile menu.
- [x] Initialized theme early with inline script and `ui.js` click handler; toggle now sets `aria-pressed` and persists choice.
- [x] DaisyUI classes missing from compiled CSS; created `input.css` and updated Tailwind config to use the plugin's default export.
- [x] Alpine.js CDN blocked during tests; vendored `alpine.min.js` locally and updated templates to reference it.
