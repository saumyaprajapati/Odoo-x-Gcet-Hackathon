# ---------- IMPORTS ----------
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from uuid import uuid4


# ---------- APP SETUP ----------
app = FastAPI()

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Firebase connection
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


# ---------- AUTH ----------
from datetime import datetime

from datetime import datetime

def generate_employee_id(first_name: str, last_name: str):
    year = datetime.now().year

    doc_ref = db.collection("company_config").document("default")
    snapshot = doc_ref.get()

    if not snapshot.exists:
        raise Exception("Company config missing")

    data = snapshot.to_dict()

    company_name = data["company_name"]
    stored_year = data["current_year"]
    serial = data["current_serial"]

    # Reset or increment serial
    if stored_year != year:
        serial = 1
        doc_ref.update({
            "current_year": year,
            "current_serial": serial
        })
    else:
        serial += 1
        doc_ref.update({
            "current_serial": serial
        })

    # 🔑 TAKE FIRST 2 LETTERS SAFELY
    first_part = first_name[:2].upper()
    last_part = last_name[:2].upper()

    employee_id = (
        company_name.upper()
        + first_part
        + last_part
        + str(year)
        + str(serial).zfill(4)
    )

    return employee_id


@app.post("/signup")
def signup(user: dict):
    # 1️⃣ Validate required fields
    required_fields = ["first_name", "last_name", "email", "password", "role"]
    for field in required_fields:
        if field not in user or not user[field]:
            return {
                "status": "error",
                "message": f"Missing field: {field}"
            }

    # 2️⃣ Check if email already exists
    existing_users = (
        db.collection("users")
        .where("email", "==", user["email"])
        .stream()
    )

    for _ in existing_users:
        return {
            "status": "error",
            "message": "User with this email already exists"
        }

    # 3️⃣ Generate employee ID (business ID)
    employee_id = generate_employee_id(
        user["first_name"],
        user["last_name"]
    )

    # 4️⃣ Generate internal system ID
    user_id = str(uuid4())

    # 5️⃣ Prepare user data (Firestore auto-creates fields)
    user_data = {
        "id": user_id,
        "employee_id": employee_id,
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "email": user["email"],
        "password": user["password"],  # hackathon-safe
        "role": user["role"],
        "year_of_joining": datetime.now().year,
        "created_at": firestore.SERVER_TIMESTAMP
    }

    # 6️⃣ Store user in Firestore
    db.collection("users").document(user_id).set(user_data)

    # 7️⃣ Send response to frontend
    return {
        "status": "success",
        "message": "User registered successfully",
        "user": {
            "id": user_id,
            "employee_id": employee_id,
            "email": user["email"],
            "role": user["role"]
        }
    }

@app.post("/login")
def login(data: dict):
    """
    Input  : email, password
    Output : user details if credentials are valid
    """

    # 1️⃣ Validate input
    if "email" not in data or "password" not in data:
        return {
            "status": "error",
            "message": "Email and password are required"
        }

    # 2️⃣ Fetch user by email
    users_ref = (
        db.collection("users")
        .where("email", "==", data["email"])
        .stream()
    )

    # 3️⃣ Verify password
    for user in users_ref:
        user_data = user.to_dict()

        if user_data["password"] == data["password"]:
            return {
                "status": "success",
                "message": "Login successful",
                "user": {
                    "id": user_data["id"],
                    "employee_id": user_data["employee_id"],
                    "first_name": user_data["first_name"],
                    "last_name": user_data["last_name"],
                    "email": user_data["email"],
                    "role": user_data["role"]
                }
            }

    # 4️⃣ If no match found
    return {
        "status": "error",
        "message": "Invalid email or password"
    }


# ---------- LEAVE MANAGEMENT ----------

# ---------- ATTENDANCE ----------
