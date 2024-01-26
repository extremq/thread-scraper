import gspread
from driver import Driver

gc = gspread.service_account(filename='credentials.json')

wks = gc.open_by_key("1KctbLFz694v9Edim6RHOypb1VZIEuANp3F0tTaRnusY").sheet1

print("Succesfully opened spreadsheet!")

driver = Driver()
driver.login("username", "password")

for i in range(1, 6146):
    print(f"Getting page {i}")
    messages = driver.get_messages_from_page(i)
    for message in messages:
        wks.append_row(values=[message.id, message.username, message.timestamp.isoformat(), message.content, message.likes])