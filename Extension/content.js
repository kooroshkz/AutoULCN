// Cross-browser compatibility
const browserAPI = typeof browser !== 'undefined' ? browser : chrome;

const detectAndSaveSecretKey = () => {
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.target.classList.contains('display') && mutation.target.innerText !== '••••••••••••••••') {
                const secretKey = mutation.target.innerText;
                browserAPI.storage.local.set({ Secret_Key: secretKey }, () => {
                    showSecretKeyNotification(secretKey);
                });
                observer.disconnect();
            }
        });
    });

    const spanElement = document.querySelector('[data-hidden-value] > .display');
    if (spanElement) {
        observer.observe(spanElement, { childList: true });
    }
};

const showSecretKeyNotification = (secretKey) => {
    const notificationDiv = document.createElement('div');
    notificationDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 16px 20px;
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        z-index: 99999;
        border-radius: 12px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        font-size: 14px;
        font-weight: 500;
        box-shadow: 0 10px 25px rgba(16, 185, 129, 0.3);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        transform: translateX(400px);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        max-width: 300px;
        word-wrap: break-word;
    `;

    const icon = document.createElement('span');
    icon.style.cssText = `
        display: inline-block;
        margin-right: 8px;
        font-size: 16px;
    `;
    icon.textContent = '🔐';

    const message = document.createElement('span');
    message.innerHTML = `<strong>Secret Key Detected!</strong><br><small style="opacity: 0.9;">${secretKey.substring(0, 8)}...</small>`;

    notificationDiv.appendChild(icon);
    notificationDiv.appendChild(message);
    document.body.appendChild(notificationDiv);

    // Animate in
    requestAnimationFrame(() => {
        notificationDiv.style.transform = 'translateX(0)';
    });

    // Animate out
    setTimeout(() => {
        notificationDiv.style.transform = 'translateX(400px)';
        notificationDiv.style.opacity = '0';
        setTimeout(() => {
            if (notificationDiv.parentNode) {
                notificationDiv.remove();
            }
        }, 400);
    }, 4000);
};

if (document.readyState === 'complete' || document.readyState === 'interactive') {
    detectAndSaveSecretKey();
} else {
    document.addEventListener('DOMContentLoaded', detectAndSaveSecretKey);
}
