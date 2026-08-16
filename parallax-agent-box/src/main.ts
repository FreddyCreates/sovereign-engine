import { revenueCat } from './revenuecat_service.js';
import { PaywallModal } from './paywall_modal.js';

document.addEventListener('DOMContentLoaded', () => {
    
    // UI Elements
    const btnOpenPaywall = document.getElementById('btn-open-paywall');
    const navSubStatus = document.getElementById('nav-subscription-status');

    const paywallModal = new PaywallModal();

    // Paywall Trigger
    btnOpenPaywall?.addEventListener('click', () => {
        paywallModal.render();
    });

    // RevenueCat Subscriber Entitlement Listener
    revenueCat.subscribe(info => {
        if (navSubStatus) {
            navSubStatus.textContent = info.isPro ? '★ Pro Member' : 'Standard Tier';
            navSubStatus.style.color = info.isPro ? '#00e676' : 'var(--text-dim)';
        }
    });

    const btnTestCheckout = document.getElementById('btn-test-checkout');
    const btnGenerateApp = document.getElementById('btn-generate-app');
    const geminiPrompt = document.getElementById('gemini-app-prompt') as HTMLInputElement;
    const geminiTerm = document.getElementById('gemini-term-output');

    // Gemini Single-Session App Generator Handler
    btnGenerateApp?.addEventListener('click', () => {
        const promptText = geminiPrompt?.value.trim() || "AI Productivity & Habit Tracker App";
        if (!geminiTerm) return;

        geminiTerm.style.display = 'block';
        geminiTerm.innerHTML = '';

        function logLine(msg: string) {
            const div = document.createElement('div');
            div.className = 'log-line';
            div.textContent = `> ${msg}`;
            geminiTerm?.appendChild(div);
            geminiTerm!.scrollTop = geminiTerm!.scrollHeight;
        }

        logLine(`[Gemini AI 3.6] Starting Single-Session App Generation: "${promptText}"`);
        (btnGenerateApp as HTMLButtonElement).disabled = true;

        setTimeout(() => logLine('Synthesizing App Architecture & UI Components...'), 400);
        setTimeout(() => logLine('Generating Motoko On-Chain Staking Canister...'), 900);
        setTimeout(() => logLine('Configuring RevenueCat Entitlements (pro_access, unlimited_ai)...'), 1500);
        setTimeout(() => logLine('Building RevenueCat Paywalls v2 Layout & 7-Day Trial Offerings...'), 2100);
        setTimeout(() => logLine('Optimizing Purchasing Power Parity (PPP) Pricing for 42 Countries...'), 2700);
        setTimeout(() => {
            logLine('✨ SINGLE-SESSION GENERATION COMPLETE! App & RevenueCat Stack Deployed.');
            (btnGenerateApp as HTMLButtonElement).disabled = false;
        }, 3400);
    });

    btnTestCheckout?.addEventListener('click', () => {
        paywallModal.render();
    });

    // Navigation Tabs Toggle
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            navItems.forEach(n => n.classList.remove('active'));
            (e.target as HTMLElement).classList.add('active');
        });
    });

    // Copilot Toggle Switches
    const toggles = document.querySelectorAll('.toggle-switch input');
    toggles.forEach(toggle => {
        toggle.addEventListener('change', (e) => {
            const input = e.target as HTMLInputElement;
            const card = input.closest('.copilot-card');
            const badge = card?.querySelector('.copilot-badge');
            
            if (badge) {
                if (input.checked) {
                    badge.textContent = 'RUNNING';
                    badge.className = 'copilot-badge badge-green';
                } else {
                    badge.textContent = 'PAUSED';
                    badge.className = 'copilot-badge';
                    (badge as HTMLElement).style.background = 'rgba(255,255,255,0.1)';
                    (badge as HTMLElement).style.color = '#888';
                }
            }
        });
    });

});
