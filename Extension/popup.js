// popup.js
chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
    const currentTab = tabs[0];
    const isGoogle = currentTab.url.includes("google.com");
  
    if (isGoogle) {
      document.getElementById("status").textContent = "You're in Google";
    } else {
      document.getElementById("status").textContent = "You're not in Google";
    }
  });
  