const user = JSON.parse(localStorage.getItem("user"));

if (!user) {
  window.location.href = "login.html";
}

document.getElementById("username").innerText =
  user.first_name + " " + user.last_name;

function logout() {
  localStorage.clear();
  window.location.href = "login.html";
}
