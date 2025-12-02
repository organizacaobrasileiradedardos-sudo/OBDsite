import requests
import json

tdid = "t_pllv_2222"
entry_url = 'https://tk2-228-23746.vs.sakura.ne.jp/n01/tournament/n01_tournament.php'

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
    'Origin': 'https://n01darts.com',
    'Referer': 'https://n01darts.com/',
    'Content-Type': 'application/json' # JS uses JSON.stringify, so likely expects JSON content type or just body
}

print(f"Fetching tournament data for {tdid}...")
try:
    # JS: url: n01_data.phpTournament + '?cmd=get_data', data: JSON.stringify({tdid: tdid,})
    response = requests.post(
        entry_url, 
        params={'cmd': 'get_data'}, 
        data=json.dumps({'tdid': tdid}),
        headers=headers
    )
    print(f"Status Code: {response.status_code}")
    try:
        data = response.json()
        print("Response Keys:", data.keys())
        if 'title' in data:
            print(f"Tournament Title: {data['title']}")
        else:
            print("Title not found in response")
            print(data)
    except json.JSONDecodeError:
        print("Response is not JSON")
        print(response.text[:500])
except Exception as e:
    print(f"Error fetching data: {e}")
