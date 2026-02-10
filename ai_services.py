import requests

LARAVEL_API = "http://127.0.0.1:8000/api"

def get_ai_data(twilio_number: str):
    """
    Fetch AI configuration and specialists for a given Twilio number.
    """
    ai_config = None
    specialists = []

    # URL encode the number (important for + sign)
    twilio_number_encoded = requests.utils.quote(twilio_number)

    # --- Fetch AI configuration ---
    try:
        res = requests.get(f"{LARAVEL_API}/ai-assistant/by-number/{twilio_number_encoded}", timeout=10)
        if res.status_code == 200:
            ai_config = res.json()
            print("\n=== AI Config Retrieved ===")
            print(ai_config)  # ✅ Print AI config
            print("===========================\n")
    except Exception as e:
        print("Error fetching AI config:", e)

    # --- If AI config exists AND role is medical assistant, fetch specialists ---
    if ai_config and ai_config.get("exists") and ai_config.get("role", "").lower() == "medical assistant":
        user_id = ai_config["user_id"]
        try:
            res = requests.get(f"{LARAVEL_API}/specialists/{user_id}", timeout=10)
            if res.status_code == 200:
                specialists = res.json()
                # ✅ Print specialists list
                print("\n=== Specialists Retrieved ===")
                for idx, doc in enumerate(specialists, start=1):
                    print(f"{idx}. Doctor Name: {doc['doctor_name']}")
                    print(f"   Speciality: {doc['specialities']}")
                    print(f"   Calendar ID: {doc['calendar_id']}\n")
                print("==============================\n")
        except Exception as e:
            print("Error fetching specialists:", e)

    return {
        "ai_config": ai_config,
        "specialists": specialists
    }

# -----------------------------
# Example usage for testing
# -----------------------------
if __name__ == "__main__":
    TWILIO_NUMBER = "+41225391848"  # replace with your number
    data = get_ai_data(TWILIO_NUMBER)
    print("Final returned data:", data)
