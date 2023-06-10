import requests
import json
import base64

#name = input("Insert name to Register")
#password = input("Insert password to Register")

name = 'miro'
password = 'miro'
# Example data
data = {
    'username': name,
    'password': password
}

# Set the Content-Type header to application/json
headers = {'Content-Type': 'application/json'}

# Send the POST request with JSON data and headers
response = requests.post('http://127.0.0.1:7777/register', data=json.dumps(data), headers=headers)

# Print the response
print(response.json())

#######################################################################################################

#name = input("Insert name to Login")
#password = input("Insert password to Login")

# Example data
data = {
    'username': name,
    'password': password
}

# Set the Content-Type header to application/json
headers = {'Content-Type': 'application/json'}

# Send the POST request with JSON data and headers
response = requests.post('http://127.0.0.1:7777/login', data=json.dumps(data), headers=headers)

session_cookie = response.cookies.get('session')

cookies_create_entry = {
    'session': session_cookie
}
# Print the response
print(response.json())

#######################################################################################################

#name = input("Insert name to Insert Image")
#password = input("Insert password to Insert Image")
# Assuming the data is stored in a file named "IMG_9071.jpg"
with open('IMG_9071.jpg', 'rb') as image_file:
    image_data = base64.b64encode(image_file.read()).decode('utf-8')

print(image_data)
#image_data = open('IMG_9071.jpg', 'rb')

payload = {
    'name': 'FirstImage'
}
files = {'image_data': open('IMG_9071.jpg','rb')}
#files = {
#    'image_data': ('IMG_9071.jpg', image_data, 'image/jpeg')
#}

headers = {
    'Content-Type': 'multipart/form-data; boundary=--boundary'
}
auth = (name, password)
response = requests.post(url='http://127.0.0.1:7777/create_entry', files=files,data=payload, headers = headers, cookies=cookies_create_entry)

try:
    response.raise_for_status()  # Raise an exception if the response has an error status code

    # Assuming the server responds with JSON data
    response_json = response.json()
    print(response_json)
except requests.exceptions.HTTPError as e:
    print("HTTP Error:", e)
    print("Response Status Code:", response.status_code)
    print("Response Content:", response.content)
except ValueError as e:
    print("Invalid JSON response:", e)
    print("Response Content:", response.content)
#finally:
    # Remember to close the file after use
    #image_data.close()

