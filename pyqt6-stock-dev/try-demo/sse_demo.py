import json
import pprint
import sseclient

def with_urllib3(url, headers):
    """Get a streaming response for the given event feed using urllib3."""
    import urllib3
    http = urllib3.PoolManager()
    return http.request('GET', url, preload_content=False, headers=headers)

def with_requests(url, headers):
    """Get a streaming response for the given event feed using requests."""
    import requests
    return requests.get(url, stream=True, headers=headers)

def with_httpx(url, headers):
    """Get a streaming response for the given event feed using httpx."""
    import httpx
    with httpx.stream('GET', url, headers=headers) as s:
        # Note: 'yield from' is Python >= 3.3. Use for/yield instead if you
        # are using an earlier version.
        yield from s.iter_bytes()


url='http://16.push2.eastmoney.com/api/qt/stock/details/sse?fields1=f1,f2,f3,f4&fields2=f51,f52,f53,f54,f55&mpi=2000&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&pos=-0&secid=0.300026'
headers = {'Accept': 'text/event-stream'}
response = with_urllib3(url, headers)  # or with_requests(url, headers)
client = sseclient.SSEClient(response)
for event in client.events():
    pprint.pprint(json.loads(event.data))
