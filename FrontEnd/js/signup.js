async function signup() {
  const first_name = document.getElementById("first_name").value;
  const last_name = document.getElementById("last_name").value;
  const email = document.getElementById("email").value;
  const role = document.getElementById("role").value;

  const res = await fetch("http://127.0.0.1:8000/signup", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ first_name, last_name, email, role })
  });

  const data = await res.json();

  if (data.status === "success") {
    alert(
      `Employee ID: ${data.credentials.employee_id}\nPassword: ${data.credentials.password}`
    );
  } else {
    alert(data.message);
  }
}
