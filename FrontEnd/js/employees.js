async function loadEmployees() {
  const res = await fetch("http://127.0.0.1:8000/employees");
  const data = await res.json();

  const container = document.getElementById("employeeList");
  container.innerHTML = "";

  data.employees.forEach(emp => {
    const card = document.createElement("div");
    card.innerHTML = `
      <h4>${emp.name}</h4>
      <p>${emp.email}</p>
      <p>Status: ${emp.status}</p>
    `;
    container.appendChild(card);
  });
}
