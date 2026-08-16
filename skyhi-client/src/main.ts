document.addEventListener('DOMContentLoaded', () => {
    
    // Simulate Terminal Output
    const termBody = document.querySelector('.term-body') as HTMLElement;
    const bridgeLogs = [
        "> Establishing TRACE link to Enterprise-OS...",
        "> Handshake accepted (AES-256).",
        "> Bridging Wyoming AI to Parallax Core...",
        "> Phantom Wallet vault secured.",
        "> Educational Platform mapping synthesized.",
        "> SYSTEM ONLINE. Welcome to Sovereign Mainnet."
    ];

    let delay = 2000;
    bridgeLogs.forEach((logText, index) => {
        setTimeout(() => {
            const line = document.createElement('div');
            line.className = 'term-line';
            line.textContent = logText;
            
            // Insert before the blinking cursor
            const cursor = document.querySelector('.blink');
            if (cursor && cursor.parentNode) {
                cursor.parentNode.insertBefore(line, cursor);
            }
            termBody.scrollTop = termBody.scrollHeight;
        }, delay);
        delay += 1200 + Math.random() * 800; // Random interval
    });

    // App Launch Interactions
    const launchBtns = document.querySelectorAll('.launch-btn');
    launchBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const target = e.target as HTMLButtonElement;
            const originalText = target.textContent || "LAUNCH";
            
            target.textContent = "INITIALIZING...";
            target.style.background = "#00e676";
            
            setTimeout(() => {
                target.textContent = "CONNECTED";
            }, 1500);
        });
    });

});
