import gspread
from driver import Driver

username = input("Username: ")
password = input("Password: ")
start_page = int(input("Start page: "))
end_page = int(input("End page: "))

gc = gspread.service_account(filename='credentials.json')
wks = gc.open_by_key("1KctbLFz694v9Edim6RHOypb1VZIEuANp3F0tTaRnusY").sheet1
print("Succesfully opened spreadsheet!")

driver = Driver()
driver.login(username, password)

for i in range(start_page, end_page + 1):
    print(f"Getting page {i}")
    messages = driver.get_messages_from_page(i)
    print(f"Messages parsed. Appending to spreadsheet...")
    values = []
    for message in messages:
        values.append([message.id, message.username, message.timestamp.isoformat(), message.content, message.likes])

    wks.append_rows(values)
