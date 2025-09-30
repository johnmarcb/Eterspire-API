import requests
from bs4 import BeautifulSoup

url = "https://eterspire.wiki/index.php/Spiderfang_Gear"
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

# Save the HTML we're actually getting
with open('actual_response.html', 'w', encoding='utf-8') as f:
    f.write(soup.prettify())

print(f"Status code: {response.status_code}")
print(f"Content length: {len(response.content)}")

# Try different ways to find tables
print(f"\nTables with class='wikitable': {len(soup.find_all('table', class_='wikitable'))}")
print(f"All tables: {len(soup.find_all('table'))}")

# Check what we're actually getting
content_div = soup.find('div', {'id': 'mw-content-text'})
if content_div:
    print(f"\nFound content div, length: {len(str(content_div))}")
    tables_in_content = content_div.find_all('table')
    print(f"Tables in content div: {len(tables_in_content)}")
else:
    print("\nNo content div found!")

# Show first 1000 chars of body
print(f"\nFirst 1000 chars of response:\n{response.text[:1000]}")