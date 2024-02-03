document.getElementById('autoFillButton').addEventListener('click', function () {
    chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
        const tab = tabs[0];
        if (tab.url.includes("login.uaccess.leidenuniv.nl")) {
            chrome.scripting.executeScript({
                target: { tabId: tab.id },
                function: function () {
                    // Fill in the form fields
                    document.querySelector('input[name="Ecom_User_ID"]').value = 'Hello';
                    document.querySelector('input[name="Ecom_Password"]').value = 'Hello123';

                    // Submit the form
                    document.querySelector('button[name="login"]').click();
                }
            });
        }
    });
});
