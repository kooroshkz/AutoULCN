// popup.js
chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
    const currentTab = tabs[0];
    const isGoogle = currentTab.url.includes("google.com");
    const storedString = localStorage.getItem("userString");
  
    const statusElement = document.getElementById("status");
    const userInputElement = document.getElementById("userInput");
    const saveButton = document.getElementById("saveButton");
  
    if (isGoogle) {
      if (storedString) {
        statusElement.textContent = "Stored String: " + storedString;
        userInputElement.style.display = "none";
        saveButton.style.display = "none"; // Hide the input and button when there's a stored string
      } else {
        statusElement.textContent = "No stored string. Enter one:";
        userInputElement.style.display = "block";
        saveButton.style.display = "block"; // Show the input and button when there's no stored string
      }
    } else {
      statusElement.textContent = "You're not in Google";
      userInputElement.style.display = "none";
      saveButton.style.display = "none"; // Hide the input and button when not on google.com
    }
  });
  
  function saveString() {
    const userInput = document.getElementById("userInput").value;
    localStorage.setItem("userString", userInput);
    document.getElementById("status").textContent = "Stored String: " + userInput;
    document.getElementById("userInput").style.display = "none";
    document.getElementById("saveButton").style.display = "none"; // Hide the input and button after saving
  }
  