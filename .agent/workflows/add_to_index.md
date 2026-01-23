---
description: Ensure all new pages are added to the project index
---
When creating ANY new HTML file or page (including email templates, widgets, or concept pages), you MUST:

1.  **Add to Index**: immediately add a link to the new file in `index.html`.
    -   Find the appropriate category card (e.g., "Виджет оплаты", "Двухдневка в Альпы", etc.).
    -   If no category fits, add it to "📂 Docs & Misc" or create a new card.
    -   Use a descriptive link text.
    -   Example: `<li><a href="Folder/NewFile.html" class="link">New Page Title</a></li>`

2.  **Verify**: Ensure the link works and the path is relative and correct.

3.  **Deploy**: This usually happens as part of the standard auto-deploy workflow, but ensure the `index.html` change is included in the commit.
