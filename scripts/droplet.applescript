on run
    -- This handles DOUBLE CLICK
    try
        do shell script "/usr/bin/python3 \"/Users/dmitry/Documents/Kover Antigravity /scripts/finder_uploader.py\""
    on error errMsg
        display dialog "Error: " & errMsg buttons {"OK"} with icon stop
    end try
end run

on open droppedItems
    -- This handles DRAG AND DROP
    set filePaths to ""
    repeat with itemRef in droppedItems
        set filePaths to filePaths & " " & (quoted form of (POSIX path of itemRef))
    end repeat
    
    try
        do shell script "/usr/bin/python3 \"/Users/dmitry/Documents/Kover Antigravity /scripts/finder_uploader.py\"" & filePaths
    on error errMsg
        display dialog "Error processing files: " & errMsg buttons {"OK"} with icon stop
    end try
end open
