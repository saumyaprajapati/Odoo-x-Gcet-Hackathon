// ===============================
// LOAD PROFILE ON PAGE LOAD
// ===============================
const user = JSON.parse(localStorage.getItem("user"));

if (!user) {
  window.location.href = "login.html";
}

async function loadProfile() {
  const res = await fetch(
    `http://127.0.0.1:8000/profile/${user.employee_id}`
  );
  const data = await res.json();

  if (data.status !== "success") {
    alert("Failed to load profile");
    return;
  }

  const p = data.profile;

  // ---------------- BASIC INFO ----------------
  document.getElementById("profileName").innerText =
    p.first_name + " " + p.last_name;

  document.getElementById("profileEmail").innerText = p.email;

  if (p.profile) {
    document.getElementById("jobPosition").innerText =
      p.profile.job_position || "-";
    document.getElementById("companyName").innerText =
      p.profile.company_name || "-";
    document.getElementById("department").innerText =
      p.profile.department || "-";
    document.getElementById("manager").innerText =
      p.profile.manager || "-";
    document.getElementById("location").innerText =
      p.profile.location || "-";
  }

  // ---------------- PRIVATE INFO ----------------
  if (p.private_info) {
    document.getElementById("dob").innerText = p.private_info.dob || "-";
    document.getElementById("address").innerText =
      p.private_info.address || "-";
    document.getElementById("nationality").innerText =
      p.private_info.nationality || "-";
    document.getElementById("personalEmail").innerText =
      p.private_info.personal_email || "-";
    document.getElementById("gender").innerText =
      p.private_info.gender || "-";
    document.getElementById("maritalStatus").innerText =
      p.private_info.marital_status || "-";
    document.getElementById("doj").innerText =
      p.private_info.date_of_joining || "-";
  }

  // ---------------- BANK INFO (VIEW ONLY) ----------------
  if (p.bank_info) {
    document.getElementById("bankAccount").innerText =
      p.bank_info.account_number || "-";
    document.getElementById("bankName").innerText =
      p.bank_info.bank_name || "-";
    document.getElementById("ifsc").innerText = p.bank_info.ifsc || "-";
    document.getElementById("pan").innerText = p.bank_info.pan || "-";
    document.getElementById("uan").innerText = p.bank_info.uan || "-";
    document.getElementById("empCode").innerText =
      p.bank_info.emp_code || "-";
  }

  // ---------------- RESUME INFO ----------------
  if (p.resume_info) {
    document.getElementById("about").innerText =
      p.resume_info.about || "";
    document.getElementById("loveJob").innerText =
      p.resume_info.love_about_job || "";
    document.getElementById("interests").innerText =
      p.resume_info.interests || "";

    renderList("skillsList", p.resume_info.skills || []);
    renderList(
      "certificationsList",
      p.resume_info.certifications || []
    );
  }

  // ---------------- SALARY (ADMIN ONLY) ----------------
  if (user.role === "admin" && p.salary_info) {
    document.getElementById("monthlyWage").innerText =
      p.salary_info.monthly_wage || "-";
    document.getElementById("yearlyWage").innerText =
      p.salary_info.yearly_wage || "-";
  }
}

// ===============================
// HELPERS
// ===============================
function renderList(elementId, items) {
  const ul = document.getElementById(elementId);
  ul.innerHTML = "";

  items.forEach((item) => {
    const li = document.createElement("li");
    li.innerText = item;
    ul.appendChild(li);
  });
}

// ===============================
// UPDATE PRIVATE INFO (EMPLOYEE)
// ===============================
async function updatePrivateInfo() {
  const payload = {
    employee_id: user.employee_id,
    private_info: {
      dob: document.getElementById("dobInput").value,
      address: document.getElementById("addressInput").value,
      nationality: document.getElementById("nationalityInput").value,
      personal_email: document.getElementById("personalEmailInput").value,
      gender: document.getElementById("genderInput").value,
      marital_status: document.getElementById("maritalStatusInput").value,
      date_of_joining: document.getElementById("dojInput").value
    }
  };

  const res = await fetch(
    "http://127.0.0.1:8000/profile/update/private",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    }
  );

  const data = await res.json();
  alert(data.status === "success" ? "Updated" : data.message);
}

// ===============================
// ADD SKILL (ADMIN OR EMPLOYEE)
// ===============================
async function addSkill() {
  const skill = document.getElementById("newSkill").value;
  if (!skill) return;

  const res = await fetch(
    `http://127.0.0.1:8000/profile/${user.employee_id}`
  );
  const data = await res.json();

  const resume = data.profile.resume_info || {};
  const skills = resume.skills || [];
  skills.push(skill);

  await fetch("http://127.0.0.1:8000/profile/update/resume", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      employee_id: user.employee_id,
      resume_info: { ...resume, skills }
    })
  });

  loadProfile();
}

// ===============================
loadProfile();
