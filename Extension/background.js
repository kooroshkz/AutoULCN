// background.js
chrome.runtime.onInstalled.addListener(function () {
    chrome.action.onClicked.addListener(async (tab) => {
      chrome.scripting.executeScript({
        target: { tabId: tab.id },
        function: () => {
          // No code needed here for this specific functionality.
        },
      });
    });
  });
  