const user = JSON.parse(localStorage.getItem("user"));

if (!user || user.role !== "admin") {
  window.location.href = "login.html";
}

// ===============================
// LOAD ALL LEAVE REQUESTS
// ===============================
async function loadLeaves() {
  const res = await fetch("http://127.0.0.1:8000/admin/leaves");
  const data = await res.json();

  const container = document.getElementById("leaveContainer");
  container.innerHTML = "";

  if (data.leaves.length === 0) {
    container.innerHTML = "<p>No leave requests</p>";
    return;
  }

  data.leaves.forEach((leave) => {
    const div = document.createElement("div");
    div.className = "leave-card";

    div.innerHTML = `
      <h4>${leave.employee_name}</h4>
      <p><b>Type:</b> ${leave.leave_type}</p>
      <p><b>From:</b> ${leave.from_date}</p>
      <p><b>To:</b> ${leave.to_date}</p>
      <p><b>Reason:</b> ${leave.reason}</p>
      <p><b>Status:</b> ${leave.status}</p>

      ${
        leave.status === "pending"
          ? `
        <button onclick="updateLeave('${leave.leave_id}', 'approved')">
          Approve
        </button>
        <button onclick="updateLeave('${leave.leave_id}', 'rejected')">
          Reject
        </button>
      `
          : ""
      }
    `;

    container.appendChild(div);
  });
}

// ===============================
// APPROVE / REJECT LEAVE
// ===============================
async function updateLeave(leaveId, status) {
  const res = await fetch(
    "http://127.0.0.1:8000/admin/leave/update",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        leave_id: leaveId,
        status: status
      })
    }
  );

  const data = await res.json();
  alert(data.message);

  loadLeaves(); // refresh list
}

// ===============================
loadLeaves();
