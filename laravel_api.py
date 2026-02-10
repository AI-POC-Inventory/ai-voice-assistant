# import requests

# LARAVEL_BASE_URL = "http://localhost:8000/api"
# DEFAULT_USER_ID = "3996"

# def get_specialists(user_id=DEFAULT_USER_ID):
#     url = f"{LARAVEL_BASE_URL}/specialists/{user_id}"
#     response = requests.get(url, timeout=10)

#     if response.status_code != 200:
#         print("Laravel API error:", response.status_code, response.text)

#     response.raise_for_status()
#     return response.json()

