const form = document.querySelector("#loadForm");
const result = document.querySelector("#result");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  result.textContent = "Checking FSOS demo match...";
  try {
    const response = await fetch("http://127.0.0.1:8080/v1/demo/match");
    const payload = await response.json();
    result.textContent = JSON.stringify(payload, null, 2);
  } catch (error) {
    result.textContent = "API unavailable. Start it with: fsos serve --port 8080";
  }
});

