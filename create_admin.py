import requests

url = "http://localhost:8000/api/users/register"
admin_data = {
    "username": "Goraya",
    "email": "admin@example.com",
    "password": "Friends@87",
    "name": "Admin Goraya",
    "role": "ADMIN",
    "registration_number": "ADMIN001",
    "department": "Administration",
    "address": "Admin Office",
    "city": "Admin City",
    "country": "Adminland",
    "phone": "+1234567890",
    "bio": "System administrator"
}

response = requests.post(url, json=admin_data)
print(response.status_code, response.json()) 