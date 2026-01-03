const user = JSON.parse(localStorage.getItem("user"));

if (!user || user.role !== "admin") {
  window.location.href = "login.html";
}

// ===============================
// LOAD SALARY INFO
// ===============================
async function loadSalary(employeeId) {
  const res = await fetch(
    `http://127.0.0.1:8000/admin/salary/${employeeId}`
  );
  const data = await res.json();

  if (data.status !== "success") {
    alert("Salary info not found");
    return;
  }

  const s = data.salary_info;

  // ---- BASIC SALARY INFO ----
  document.getElementById("monthlyWage").innerText =
    s.monthly_wage || "-";
  document.getElementById("yearlyWage").innerText =
    s.yearly_wage || "-";
  document.getElementById("workingDays").innerText =
    s.working_days_per_week || "-";
  document.getElementById("breakTime").innerText =
    s.break_time_hours || "-";

  // ---- SALARY COMPONENTS ----
  if (s.components) {
    document.getElementById("basicSalary").innerText =
      s.components.basic_amount || "-";
    document.getElementById("hra").innerText =
      s.components.hra_amount || "-";
    document.getElementById("standardAllowance").innerText =
      s.components.standard_allowance || "-";
    document.getElementById("performanceBonus").innerText =
      s.components.performance_bonus_amount || "-";
    document.getElementById("lta").innerText =
      s.components.leave_travel_allowance_amount || "-";
    document.getElementById("fixedAllowance").innerText =
      s.components.fixed_allowance || "-";
  }

  // ---- PF CONTRIBUTION ----
  if (s.components && s.components.pf) {
    document.getElementById("pfEmployee").innerText =
      s.components.pf.employee_amount || "-";
    document.getElementById("pfEmployer").innerText =
      s.components.pf.employer_amount || "-";
  }

  // ---- TAX ----
  if (s.tax) {
    document.getElementById("professionalTax").innerText =
      s.tax.professional_tax || "-";
  }
}
