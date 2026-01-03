async function checkIn() {
  const user = JSON.parse(localStorage.getItem("user"));

  const res = await fetch("http://127.0.0.1:8000/attendance/check-in", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      employee_id: user.employee_id,
      employee_name: user.first_name + " " + user.last_name
    })
  });

  const data = await res.json();
  alert(data.message);
}

async function checkOut() {
  const user = JSON.parse(localStorage.getItem("user"));

  const res = await fetch("http://127.0.0.1:8000/attendance/check-out", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      employee_id: user.employee_id
    })
  });

  const data = await res.json();
  alert(data.message);
}
