async function login() {
  const data = {
    email: document.getElementById("email").value,
    password: document.getElementById("password").value
  };

  const res = await fetch("http://127.0.0.1:8000/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data)
  });

  const result = await res.json();

  if (result.status === "success") {
    localStorage.setItem("user", JSON.stringify(result.user));

    if (result.user.role === "admin") {
      window.location.href = "admin.html";
    } else {
      window.location.href = "employee.html";
    }
  } else {
    alert(result.message);
  }
}
