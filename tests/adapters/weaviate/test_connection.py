import requests

url = "http://localhost:8080/v1/.well-known/ready"
res = requests.get(url)

if res.status_code == 200:
    print("Weaviate is ready to accept Connection.")
else:
    print("Weaviate is not ready. Status:", res.status_code)
