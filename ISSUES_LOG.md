## Issues Log

- [ ] Test script fails due to network access restrictions when reaching n8n webhook.
- [ ] Netlify deployment may fail if Ollama endpoints are blocked or require authentication.
- [ ] Performance policy pages need improved responsive styling.
- [x] Netlify deploy failed to parse configuration; replaced `python_runtime` with `python_version`.
- [x] Netlify deploy still failed due to `python_version`; removed the property entirely.
- [x] Netlify deploy preview served 404s due to functions not detected; added explicit directory setting.
- [ ] Deployed site still returns 404; added base path stripping and included files for templates.
- [ ] Docker container may not honor `PORT` variable due to exec-form CMD.
