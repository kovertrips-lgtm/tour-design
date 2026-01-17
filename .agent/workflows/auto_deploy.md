---
description: Automatically deploy changes to GitHub/Vercel after edits
---

After implementing ANY code changes requested by the user (HTML, CSS, JS edits), you MUST strictly follow this procedure:

1.  **Verify Changes:** Ensure the code edits are complete and saved.
2.  **Git Add:** Run `git add .`
3.  **Git Commit:** Run `git commit -m "Auto-deploy: [Brief description of changes]"`
4.  **Git Push:** Run `git push origin main`

**CRITICAL RULE:** Do not wait for the user to ask for a deploy. Every edit session should end with a push to ensure Vercel is always up to date.
