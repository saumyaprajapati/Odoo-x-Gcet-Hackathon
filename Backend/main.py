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

import random
import string

def generate_password(company_name: str):
    letters = string.ascii_letters
    digits = string.digits
    special = "@#%&"

    random_part = (
        random.choice(letters)
        + random.choice(digits)
        + random.choice(letters)
        + random.choice(digits)
    )

    password = (
        company_name.upper()
        + "@"
        + random_part
        + random.choice(special)
    )

    return password

@app.post("/signup")
def signup(user: dict):
    required_fields = ["first_name", "last_name", "email", "role"]
    for field in required_fields:
        if field not in user or not user[field]:
            return {
                "status": "error",
                "message": f"Missing field: {field}"
            }

    # Check duplicate email
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

    # Generate IDs
    employee_id = generate_employee_id(
        user["first_name"],
        user["last_name"]
    )

    user_id = str(uuid4())

    # 🔐 Generate password automatically
    password = generate_password("OD")

    user_data = {
        "id": user_id,
        "employee_id": employee_id,
        "first_name": user["first_name"],
        "last_name": user["last_name"],
        "email": user["email"],
        "password": password,   # auto-generated
        "role": user["role"],
        "year_of_joining": datetime.now().year,
        "created_at": firestore.SERVER_TIMESTAMP
    }

    db.collection("users").document(user_id).set(user_data)

    # ⚠️ Password returned ONLY ONCE
    return {
        "status": "success",
        "message": "User created successfully",
        "credentials": {
            "employee_id": employee_id,
            "password": password
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

@app.post("/change-password")
def change_password(data: dict):
    required_fields = ["email", "old_password", "new_password"]
    for field in required_fields:
        if field not in data or not data[field]:
            return {
                "status": "error",
                "message": f"Missing field: {field}"
            }

    users_ref = (
        db.collection("users")
        .where("email", "==", data["email"])
        .stream()
    )

    for user in users_ref:
        user_data = user.to_dict()

        # Verify old password
        if user_data["password"] != data["old_password"]:
            return {
                "status": "error",
                "message": "Old password is incorrect"
            }

        # Update password
        db.collection("users").document(user.id).update({
            "password": data["new_password"]
        })

        return {
            "status": "success",
            "message": "Password changed successfully"
        }

    return {
        "status": "error",
        "message": "User not found"
    }

# ---------- LEAVE MANAGEMENT ----------

@app.post("/leave/apply")
def apply_leave(data: dict):
    required_fields = [
        "employee_id",
        "employee_name",
        "leave_type",
        "from_date",
        "to_date",
        "reason"
    ]

    for field in required_fields:
        if field not in data or not data[field]:
            return {
                "status": "error",
                "message": f"Missing field: {field}"
            }

    leave_id = str(uuid4())

    leave_data = {
        "leave_id": leave_id,
        "employee_id": data["employee_id"],
        "employee_name": data["employee_name"],
        "leave_type": data["leave_type"],
        "from_date": data["from_date"],
        "to_date": data["to_date"],
        "reason": data["reason"],
        "status": "pending",
        "applied_at": firestore.SERVER_TIMESTAMP
    }

    db.collection("leaves").document(leave_id).set(leave_data)

    return {
        "status": "success",
        "message": "Leave applied successfully",
        "leave_id": leave_id
    }

@app.get("/admin/leaves")
def get_all_leaves():
    leaves = []

    docs = db.collection("leaves").stream()

    for doc in docs:
        leaves.append(doc.to_dict())

    return {
        "status": "success",
        "leaves": leaves
    }

@app.post("/admin/leave/update")
def update_leave_status(data: dict):
    if "leave_id" not in data or "status" not in data:
        return {
            "status": "error",
            "message": "leave_id and status required"
        }

    if data["status"] not in ["approved", "rejected"]:
        return {
            "status": "error",
            "message": "Invalid status"
        }

    db.collection("leaves").document(data["leave_id"]).update({
        "status": data["status"]
    })

    return {
        "status": "success",
        "message": f"Leave {data['status']}"
    }

@app.get("/leave/my/{employee_id}")
def get_my_leaves(employee_id: str):
    leaves = []

    docs = (
        db.collection("leaves")
        .where("employee_id", "==", employee_id)
        .stream()
    )

    for doc in docs:
        leaves.append(doc.to_dict())

    return {
        "status": "success",
        "leaves": leaves
    }

# ---------- ATTENDANCE ----------
@app.post("/attendance/check-in")
def check_in(data: dict):
    if "employee_id" not in data or "employee_name" not in data:
        return {
            "status": "error",
            "message": "employee_id and employee_name required"
        }

    today = datetime.now().strftime("%Y-%m-%d")

    # Check if already checked in today
    existing = (
        db.collection("attendance")
        .where("employee_id", "==", data["employee_id"])
        .where("date", "==", today)
        .stream()
    )

    for _ in existing:
        return {
            "status": "error",
            "message": "Already checked in today"
        }

    attendance_id = str(uuid4())

    attendance_data = {
        "attendance_id": attendance_id,
        "employee_id": data["employee_id"],
        "employee_name": data["employee_name"],
        "date": today,
        "check_in": firestore.SERVER_TIMESTAMP,
        "check_out": None,
        "status": "present",
        "created_at": firestore.SERVER_TIMESTAMP
    }

    db.collection("attendance").document(attendance_id).set(attendance_data)

    return {
        "status": "success",
        "message": "Check-in successful"
    }

@app.post("/attendance/check-out")
def check_out(data: dict):
    if "employee_id" not in data:
        return {
            "status": "error",
            "message": "employee_id required"
        }

    today = datetime.now().strftime("%Y-%m-%d")

    docs = (
        db.collection("attendance")
        .where("employee_id", "==", data["employee_id"])
        .where("date", "==", today)
        .stream()
    )

    for doc in docs:
        db.collection("attendance").document(doc.id).update({
            "check_out": firestore.SERVER_TIMESTAMP
        })

        return {
            "status": "success",
            "message": "Check-out successful"
        }

    return {
        "status": "error",
        "message": "No check-in found for today"
    }

@app.get("/attendance/my/{employee_id}")
def my_attendance(employee_id: str):
    records = []

    docs = (
        db.collection("attendance")
        .where("employee_id", "==", employee_id)
        .stream()
    )

    for doc in docs:
        records.append(doc.to_dict())

    return {
        "status": "success",
        "attendance": records
    }

@app.get("/admin/attendance")
def all_attendance():
    records = []

    docs = db.collection("attendance").stream()

    for doc in docs:
        records.append(doc.to_dict())

    return {
        "status": "success",
        "attendance": records
    }

@app.get("/employees")
def get_all_employees():
    employees = []
    today = datetime.now().strftime("%Y-%m-%d")

    user_docs = db.collection("users").stream()

    for user in user_docs:
        user_data = user.to_dict()
        employee_id = user_data["employee_id"]

        # Default status
        status = "absent"

        # 1️⃣ Check attendance (present)
        attendance_docs = (
            db.collection("attendance")
            .where("employee_id", "==", employee_id)
            .where("date", "==", today)
            .stream()
        )

        for _ in attendance_docs:
            status = "present"

        # 2️⃣ Check approved leave (overrides absent)
        leave_docs = (
            db.collection("leaves")
            .where("employee_id", "==", employee_id)
            .where("status", "==", "approved")
            .stream()
        )

        for leave in leave_docs:
            leave_data = leave.to_dict()
            if leave_data["from_date"] <= today <= leave_data["to_date"]:
                status = "on_leave"

        employees.append({
            "employee_id": employee_id,
            "name": f"{user_data['first_name']} {user_data['last_name']}",
            "email": user_data["email"],
            "role": user_data["role"],
            "status": status,
            "profile_pic": "default.png"  # frontend placeholder
        })

    return {
        "status": "success",
        "employees": employees
    }

@app.get("/employee/{employee_id}")
def get_employee_profile(employee_id: str):
    docs = (
        db.collection("users")
        .where("employee_id", "==", employee_id)
        .stream()
    )

    for doc in docs:
        user = doc.to_dict()
        return {
            "status": "success",
            "employee": {
                "employee_id": user["employee_id"],
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "email": user["email"],
                "role": user["role"],
                "year_of_joining": user["year_of_joining"]
            }
        }

    return {
        "status": "error",
        "message": "Employee not found"
    }

#------
@app.get("/profile/{employee_id}")
def get_my_profile(employee_id: str):
    docs = (
        db.collection("users")
        .where("employee_id", "==", employee_id)
        .stream()
    )

    for doc in docs:
        return {
            "status": "success",
            "profile": doc.to_dict()
        }

    return {
        "status": "error",
        "message": "Profile not found"
    }

@app.post("/profile/update/basic")
def update_basic_profile(data: dict):
    required = ["employee_id", "profile"]
    for r in required:
        if r not in data:
            return {"status": "error", "message": f"Missing {r}"}

    docs = (
        db.collection("users")
        .where("employee_id", "==", data["employee_id"])
        .stream()
    )

    for doc in docs:
        db.collection("users").document(doc.id).update({
            "profile": data["profile"]
        })
        return {"status": "success"}

    return {"status": "error", "message": "User not found"}

@app.post("/profile/update/private")
def update_private_info(data: dict):
    docs = (
        db.collection("users")
        .where("employee_id", "==", data["employee_id"])
        .stream()
    )

    for doc in docs:
        db.collection("users").document(doc.id).update({
            "private_info": data["private_info"]
        })
        return {"status": "success"}

    return {"status": "error", "message": "User not found"}

@app.post("/profile/update/bank")
def update_bank_info(data: dict):
    docs = (
        db.collection("users")
        .where("employee_id", "==", data["employee_id"])
        .stream()
    )

    for doc in docs:
        db.collection("users").document(doc.id).update({
            "bank_info": data["bank_info"]
        })
        return {"status": "success"}

    return {"status": "error", "message": "User not found"}

@app.post("/profile/update/salary")
def update_salary_info(data: dict):
    if data.get("role") != "admin":
        return {"status": "error", "message": "Unauthorized"}

    docs = (
        db.collection("users")
        .where("employee_id", "==", data["employee_id"])
        .stream()
    )

    for doc in docs:
        db.collection("users").document(doc.id).update({
            "salary_info": data["salary_info"]
        })
        return {"status": "success"}

    return {"status": "error", "message": "User not found"}

@app.post("/profile/update/resume")
def update_resume_info(data: dict):
    docs = (
        db.collection("users")
        .where("employee_id", "==", data["employee_id"])
        .stream()
    )

    for doc in docs:
        db.collection("users").document(doc.id).update({
            "resume_info": data["resume_info"]
        })
        return {"status": "success"}

    return {"status": "error", "message": "User not found"}

def calculate_salary_structure(monthly_wage, config):
    basic_amount = monthly_wage * config["basic_percent"] / 100
    hra_amount = basic_amount * config["hra_percent"] / 100

    performance_bonus_amount = basic_amount * config["performance_bonus_percent"] / 100
    lta_amount = basic_amount * config["lta_percent"] / 100

    fixed_allowance = (
        monthly_wage
        - (basic_amount + hra_amount + performance_bonus_amount + lta_amount + config["standard_allowance"])
    )

    employee_pf = basic_amount * config["pf_employee_percent"] / 100
    employer_pf = basic_amount * config["pf_employer_percent"] / 100

    return {
        "basic_amount": round(basic_amount, 2),
        "hra_amount": round(hra_amount, 2),
        "performance_bonus_amount": round(performance_bonus_amount, 2),
        "leave_travel_allowance_amount": round(lta_amount, 2),
        "fixed_allowance": round(fixed_allowance, 2),
        "pf": {
            "employee_amount": round(employee_pf, 2),
            "employer_amount": round(employer_pf, 2)
        }
    }

@app.post("/admin/salary/update")
def update_salary(data: dict):
    if data.get("role") != "admin":
        return {"status": "error", "message": "Unauthorized"}

    employee_id = data["employee_id"]
    monthly_wage = data["monthly_wage"]

    config = {
        "basic_percent": data["basic_percent"],
        "hra_percent": data["hra_percent"],
        "performance_bonus_percent": data["performance_bonus_percent"],
        "lta_percent": data["lta_percent"],
        "standard_allowance": data["standard_allowance"],
        "pf_employee_percent": data["pf_employee_percent"],
        "pf_employer_percent": data["pf_employer_percent"]
    }

    computed = calculate_salary_structure(monthly_wage, config)

    docs = (
        db.collection("users")
        .where("employee_id", "==", employee_id)
        .stream()
    )

    for doc in docs:
        db.collection("users").document(doc.id).update({
            "salary_info": {
                "monthly_wage": monthly_wage,
                "yearly_wage": monthly_wage * 12,
                "components": {
                    **config,
                    **computed
                },
                "tax": {
                    "professional_tax": 200
                }
            }
        })
        return {"status": "success"}

    return {"status": "error", "message": "Employee not found"}

@app.get("/admin/salary/{employee_id}")
def get_salary(employee_id: str):
    docs = (
        db.collection("users")
        .where("employee_id", "==", employee_id)
        .stream()
    )

    for doc in docs:
        return {
            "status": "success",
            "salary_info": doc.to_dict().get("salary_info", {})
        }

    return {"status": "error", "message": "Not found"}

@app.post("/attendance/check-in")
def check_in(data: dict):
    today = datetime.now().strftime("%Y-%m-%d")

    attendance_ref = db.collection("attendance")

    # Prevent double check-in
    existing = (
        attendance_ref
        .where("employee_id", "==", data["employee_id"])
        .where("date", "==", today)
        .stream()
    )

    for _ in existing:
        return {"status": "error", "message": "Already checked in"}

    attendance_ref.add({
        "employee_id": data["employee_id"],
        "date": today,
        "check_in": datetime.now().strftime("%H:%M"),
        "check_out": None,
        "work_hours": 0,
        "extra_hours": 0,
        "break_minutes": data.get("break_minutes", 60),
        "status": "present"
    })

    return {"status": "success", "message": "Checked in"}

@app.post("/attendance/check-out")
def check_out(data: dict):
    today = datetime.now().strftime("%Y-%m-%d")

    docs = (
        db.collection("attendance")
        .where("employee_id", "==", data["employee_id"])
        .where("date", "==", today)
        .stream()
    )

    for doc in docs:
        record = doc.to_dict()
        check_in_time = datetime.strptime(record["check_in"], "%H:%M")
        check_out_time = datetime.now()

        work_hours = (check_out_time - check_in_time).seconds / 3600
        extra_hours = max(0, work_hours - 8)

        db.collection("attendance").document(doc.id).update({
            "check_out": check_out_time.strftime("%H:%M"),
            "work_hours": round(work_hours, 2),
            "extra_hours": round(extra_hours, 2)
        })

        return {"status": "success", "message": "Checked out"}

    return {"status": "error", "message": "No check-in found"}

@app.get("/attendance/employee/{employee_id}")
def employee_attendance(employee_id: str, month: int, year: int):
    records = []
    present_days = 0

    docs = (
        db.collection("attendance")
        .where("employee_id", "==", employee_id)
        .stream()
    )

    for doc in docs:
        data = doc.to_dict()
        d = datetime.strptime(data["date"], "%Y-%m-%d")

        if d.month == month and d.year == year:
            records.append(data)
            if data["status"] == "present":
                present_days += 1

    return {
        "status": "success",
        "month": month,
        "year": year,
        "present_days": present_days,
        "records": records
    }

@app.get("/attendance/admin/today")
def admin_today_attendance():
    today = datetime.now().strftime("%Y-%m-%d")
    result = []

    docs = (
        db.collection("attendance")
        .where("date", "==", today)
        .stream()
    )

    for doc in docs:
        result.append(doc.to_dict())

    return {
        "status": "success",
        "date": today,
        "attendance": result
    }

@app.get("/attendance/payable-days/{employee_id}")
def payable_days(employee_id: str, month: int, year: int):
    payable_days = 0

    docs = (
        db.collection("attendance")
        .where("employee_id", "==", employee_id)
        .stream()
    )

    for doc in docs:
        data = doc.to_dict()
        d = datetime.strptime(data["date"], "%Y-%m-%d")

        if d.month == month and d.year == year:
            if data["status"] == "present":
                payable_days += 1

    return {
        "status": "success",
        "employee_id": employee_id,
        "payable_days": payable_days
    }

@app.post("/time-off/apply")
def apply_time_off(data: dict):
    required = ["employee_id", "employee_name", "type", "start_date", "end_date"]
    for r in required:
        if r not in data:
            return {"status": "error", "message": f"Missing {r}"}

    start = datetime.strptime(data["start_date"], "%Y-%m-%d")
    end = datetime.strptime(data["end_date"], "%Y-%m-%d")
    days = (end - start).days + 1

    # Count already used leaves
    used = 0
    docs = (
        db.collection("time_off")
        .where("employee_id", "==", data["employee_id"])
        .where("type", "==", data["type"])
        .where("status", "==", "approved")
        .stream()
    )

    for d in docs:
        used += d.to_dict()["days"]

    if used + days > LEAVE_LIMITS[data["type"]]:
        return {"status": "error", "message": "Leave limit exceeded"}

    db.collection("time_off").add({
        "employee_id": data["employee_id"],
        "employee_name": data["employee_name"],
        "type": data["type"],
        "start_date": data["start_date"],
        "end_date": data["end_date"],
        "days": days,
        "status": "pending",
        "attachment": data.get("attachment"),
        "applied_at": firestore.SERVER_TIMESTAMP,
        "approved_by": None
    })

    return {"status": "success", "message": "Time off request submitted"}

@app.get("/time-off/employee/{employee_id}")
def employee_time_off(employee_id: str):
    result = []

    docs = (
        db.collection("time_off")
        .where("employee_id", "==", employee_id)
        .stream()
    )

    for doc in docs:
        result.append(doc.to_dict())

    return {
        "status": "success",
        "records": result
    }

@app.get("/time-off/admin")
def admin_time_off():
    result = []

    docs = db.collection("time_off").stream()
    for doc in docs:
        record = doc.to_dict()
        record["id"] = doc.id
        result.append(record)

    return {
        "status": "success",
        "records": result
    }

@app.post("/time-off/approve")
def approve_time_off(data: dict):
    doc_id = data["request_id"]
    admin_name = data["admin_name"]

    db.collection("time_off").document(doc_id).update({
        "status": "approved",
        "approved_by": admin_name
    })

    return {"status": "success", "message": "Approved"}

def sync_leave_to_attendance():
    today = datetime.now().strftime("%Y-%m-%d")

    docs = (
        db.collection("time_off")
        .where("status", "==", "approved")
        .stream()
    )

    for doc in docs:
        leave = doc.to_dict()
        if leave["start_date"] <= today <= leave["end_date"]:
            db.collection("attendance").add({
                "employee_id": leave["employee_id"],
                "date": today,
                "status": "on_leave",
                "check_in": None,
                "check_out": None,
                "work_hours": 0,
                "extra_hours": 0
            })
