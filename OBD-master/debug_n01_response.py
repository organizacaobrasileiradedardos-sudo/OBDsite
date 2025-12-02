import requests
import re

url = "https://n01darts.com/n01/tournament/t_stats.html?id=t_pllv_2222"
tdid = "t_pllv_2222"

# Based on n01.py logic
stats_url = 'https://tk2-228-23746.vs.sakura.ne.jp/n01/tournament/n01_stats_t.php'
entry_url = 'https://tk2-228-23746.vs.sakura.ne.jp/n01/tournament/n01_tournament.php'

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
    'Origin': 'https://n01darts.com',
    'Referer': 'https://n01darts.com/'
}

print(f"Fetching entry list for {tdid}...")
try:
    response = requests.post(entry_url, params={'cmd': 'get_entry_list', 'tdid': tdid}, headers=headers)
    data = response.json()
    print("Entry List Response Keys:", data[0].keys() if isinstance(data, list) and len(data) > 0 else "Empty or not list")
    # Check if tournament name is in the first item or somewhere else
    if isinstance(data, list) and len(data) > 0:
        print("First item sample:", data[0])
except Exception as e:
    print(f"Error fetching entry list: {e}")

print(f"\nFetching stats list for {tdid}...")
try:
    response = requests.post(stats_url, params={'cmd': 'stats_list', 'tdid': tdid}, headers=headers)
    data = response.json()
    print("Stats List Response Keys:", data.keys() if isinstance(data, dict) else "Not a dict")
    if isinstance(data, dict) and 'result' not in data: # result usually means error or empty
         print("Sample keys:", list(data.keys())[:5])
except Exception as e:
    print(f"Error fetching stats list: {e}")
