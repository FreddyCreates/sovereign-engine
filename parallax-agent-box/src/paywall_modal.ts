// paywall_modal.ts
// Interactive RevenueCat Paywall Modal Component

import { revenueCat, PackageOffer } from './revenuecat_service.js';

export class PaywallModal {
    private modalElement: HTMLElement | null = null;

    public async render() {
        if (document.getElementById('rc-paywall-modal')) return;

        const offerings = await revenueCat.getOfferings();

        const modalHtml = `
        <div class="rc-paywall-overlay" id="rc-paywall-modal">
            <div class="rc-paywall-card">
                <button class="rc-close-btn" id="rc-close-paywall">&times;</button>
                
                <div class="rc-paywall-header">
                    <div class="rc-badge-rc">Powered by RevenueCat</div>
                    <h2>UNLOCK <span>PARALLAX PRO</span></h2>
                    <p>Execute 873ms TRADEX signals, deploy unlimited TS agents & earn φ-compounding yield.</p>
                </div>

                <div class="rc-plan-selector">
                    ${offerings.map((offering, idx) => `
                        <div class="rc-plan-card ${idx === 0 ? 'selected' : ''}" data-pkg-id="${offering.id}">
                            <div class="rc-plan-tag">${offering.period === 'annual' ? 'BEST VALUE' : 'MOST POPULAR'}</div>
                            <div class="rc-plan-main">
                                <h4>${offering.title}</h4>
                                <div class="rc-plan-price">${offering.priceString}</div>
                            </div>
                            <p class="rc-plan-desc">${offering.description}</p>
                            <ul class="rc-feature-list">
                                ${offering.features.map(f => `<li><span class="check">✓</span> ${f}</li>`).join('')}
                            </ul>
                        </div>
                    `).join('')}
                </div>

                <div class="rc-paywall-footer">
                    <button class="btn btn-primary rc-checkout-btn" id="rc-btn-subscribe">
                        START 7-DAY FREE TRIAL
                    </button>
                    <div class="rc-footer-links">
                        <a href="#" id="rc-restore-purchases">Restore Purchases</a> • 
                        <span>Terms & Privacy</span>
                    </div>
                </div>
            </div>
        </div>
        `;

        const container = document.createElement('div');
        container.innerHTML = modalHtml;
        document.body.appendChild(container.firstElementChild!);

        this.modalElement = document.getElementById('rc-paywall-modal');
        this.attachEvents(offerings);
    }

    private attachEvents(offerings: PackageOffer[]) {
        if (!this.modalElement) return;

        let selectedPkg = offerings[0];

        // Close button
        document.getElementById('rc-close-paywall')?.addEventListener('click', () => {
            this.close();
        });

        // Plan Cards Selection
        const cards = this.modalElement.querySelectorAll('.rc-plan-card');
        cards.forEach(card => {
            card.addEventListener('click', (e) => {
                cards.forEach(c => c.classList.remove('selected'));
                const target = (e.currentTarget as HTMLElement);
                target.classList.add('selected');
                
                const pkgId = target.dataset.pkgId;
                const found = offerings.find(o => o.id === pkgId);
                if (found) selectedPkg = found;
            });
        });

        // Subscribe Button
        const subscribeBtn = document.getElementById('rc-btn-subscribe') as HTMLButtonElement;
        subscribeBtn?.addEventListener('click', async () => {
            subscribeBtn.disabled = true;
            subscribeBtn.textContent = 'PROCESSING PAYWALL VIA REVENUECAT...';

            try {
                await revenueCat.purchasePackage(selectedPkg);
                subscribeBtn.textContent = '✓ UNLOCKED & ACTIVE!';
                subscribeBtn.style.background = '#00e676';
                setTimeout(() => this.close(), 1200);
            } catch (err) {
                alert('Purchase error. Please try again.');
                subscribeBtn.disabled = false;
                subscribeBtn.textContent = 'START 7-DAY FREE TRIAL';
            }
        });

        // Restore Purchases
        document.getElementById('rc-restore-purchases')?.addEventListener('click', async (e) => {
            e.preventDefault();
            await revenueCat.restorePurchases();
            alert('Purchases restored successfully!');
        });
    }

    public close() {
        if (this.modalElement) {
            this.modalElement.remove();
            this.modalElement = null;
        }
    }
}
