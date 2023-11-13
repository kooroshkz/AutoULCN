// background.js
chrome.runtime.onInstalled.addListener(function () {
    chrome.action.onClicked.addListener(async (tab) => {
      await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        function: () => {
          alert("You're in Google");
        },
      });
    });
  });
  