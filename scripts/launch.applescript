tell application "Finder"
    set sel to selection
    if (count of sel) is 0 then
        display dialog "⚠️ Сначала выберите фото в Finder!" buttons {"OK"} default button "OK" with icon caution
        return
    end if
end tell

try
    do shell script "/usr/bin/python3 \"/Users/dmitry/Documents/Kover Antigravity /scripts/finder_uploader.py\""
on error errMsg
    display dialog "Ошибка: " & errMsg buttons {"OK"} with icon stop
end try
