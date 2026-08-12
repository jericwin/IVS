import requests

def upload_image():
    with open('static/images/product-1.png', 'rb') as f:
        files = {'fileToUpload': ('product-1.png', f, 'image/png')}
        data = {'reqtype': 'fileupload'}
        resp = requests.post('https://catbox.moe/user/api.php', files=files, data=data)
        print(f"Status: {resp.status_code}")
        print(f"URL: {resp.text}")

if __name__ == '__main__':
    upload_image()
