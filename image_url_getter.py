import requests
import keys

CLIENT_ID = keys.imgur_key

image_path = '/Users/aarya/Documents/SNAIC/scooter.jpg'

with open(image_path, 'rb') as img:
    image_data = img.read()

url = "https://api.imgur.com/3/image"

headers = {
    'Authorization': f'Client-ID {CLIENT_ID}'
}

payload = {
    'image': image_data,
    'type': 'file'
}

response = requests.post(url, headers=headers, files={'image': image_data})

if response.status_code == 200:
    json_response = response.json()
    image_url = json_response['data']['link']
    print(f"Image successfully uploaded: {image_url}")
else:
    print(f"Failed to upload image. Status code: {response.status_code}, Response: {response.text}")

