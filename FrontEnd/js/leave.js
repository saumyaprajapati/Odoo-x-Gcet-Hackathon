async function applyLeave() {
  const user = JSON.parse(localStorage.getItem("user"));

  const leave_type = document.getElementById("leave_type").value;
  const from_date = document.getElementById("from_date").value;
  const to_date = document.getElementById("to_date").value;
  const reason = document.getElementById("reason").value;

  const res = await fetch("http://127.0.0.1:8000/leave/apply", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      employee_id: user.employee_id,
      employee_name: user.first_name + " " + user.last_name,
      leave_type,
      from_date,
      to_date,
      reason
    })
  });

  const data = await res.json();
  alert(data.message);
}
