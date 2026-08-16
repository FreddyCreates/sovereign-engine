// revenuecat_service.ts
// Integration wrapper for RevenueCat In-App Purchases, Paywalls & Subscriptions

export interface CustomerInfo {
    activeEntitlements: string[];
    subscriberId: string;
    isPro: boolean;
    isEnterprise: boolean;
}

export interface PackageOffer {
    id: string;
    identifier: string;
    title: string;
    priceString: string;
    period: 'monthly' | 'annual';
    description: string;
    features: string[];
    entitlement: string;
}

export class RevenueCatService {
    private static instance: RevenueCatService;
    private apiKey: string = 'rcb_pub_live_parallax_sovereign_2026';
    private currentSubscriberId: string = 'usr_sovereign_' + Math.random().toString(36).substring(2, 9);
    
    private activeEntitlements: Set<string> = new Set(['free_tier']);
    private listeners: ((info: CustomerInfo) => void)[] = [];

    private constructor() {
        console.log(`[RevenueCat SDK Initialized] API Key: ${this.apiKey}`);
        // Hydrate from localStorage if available
        const saved = localStorage.getItem('parallax_entitlements');
        if (saved) {
            try {
                const parsed = JSON.parse(saved);
                parsed.forEach((e: string) => this.activeEntitlements.add(e));
            } catch (err) {
                console.error("Failed to parse saved entitlements", err);
            }
        }
    }

    public static getInstance(): RevenueCatService {
        if (!RevenueCatService.instance) {
            RevenueCatService.instance = new RevenueCatService();
        }
        return RevenueCatService.instance;
    }

    public async getOfferings(): Promise<PackageOffer[]> {
        return [
            {
                id: 'pkg_pro_monthly',
                identifier: 'parallax_pro_monthly',
                title: 'Parallax Pro',
                priceString: '$19.99 / mo',
                period: 'monthly',
                description: 'Unlock high-frequency TRADEX AGI 873ms heartbeat & custom TS bot execution.',
                features: [
                    'Continuous 873ms CLOB Execution',
                    'Phantom Signal MEV Front-Running Alerts',
                    'Unlimited Custom TS Agent Deployments',
                    '1.618x φ-Yield Staking Multiplier'
                ],
                entitlement: 'pro_access'
            },
            {
                id: 'pkg_pro_annual',
                identifier: 'parallax_pro_annual',
                title: 'Parallax Pro (Annual)',
                priceString: '$149.99 / yr',
                period: 'annual',
                description: 'Save 37% with annual φ-compounding commitment.',
                features: [
                    'All Monthly Pro Features',
                    'Priority ORO Council Voting Power',
                    '37% Discount on FORMA Swap Fees'
                ],
                entitlement: 'pro_access'
            },
            {
                id: 'pkg_enterprise_monthly',
                identifier: 'parallax_enterprise_monthly',
                title: 'Enterprise Sovereign',
                priceString: '$99.99 / mo',
                period: 'monthly',
                description: 'For institutional funds, liquidity providers & Motoko canister builders.',
                features: [
                    'Direct Motoko Subnet Canister Deployment',
                    'Dedicated 4-Agent Council Node Reservation',
                    'Custom Clearinghouse Risk Parameters',
                    '24/7 Dedicated Sovereign Protocol Support'
                ],
                entitlement: 'enterprise_access'
            }
        ];
    }

    public getCustomerInfo(): CustomerInfo {
        return {
            activeEntitlements: Array.from(this.activeEntitlements),
            subscriberId: this.currentSubscriberId,
            isPro: this.activeEntitlements.has('pro_access') || this.activeEntitlements.has('enterprise_access'),
            isEnterprise: this.activeEntitlements.has('enterprise_access')
        };
    }

    public async purchasePackage(pkg: PackageOffer): Promise<CustomerInfo> {
        console.log(`[RevenueCat] Initiating checkout for ${pkg.title} (${pkg.priceString})...`);
        
        // Simulate RevenueCat payment process
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        this.activeEntitlements.add(pkg.entitlement);
        localStorage.setItem('parallax_entitlements', JSON.stringify(Array.from(this.activeEntitlements)));

        const info = this.getCustomerInfo();
        this.notifyListeners(info);
        return info;
    }

    public async restorePurchases(): Promise<CustomerInfo> {
        console.log("[RevenueCat] Restoring purchases for subscriber:", this.currentSubscriberId);
        await new Promise(resolve => setTimeout(resolve, 1000));
        return this.getCustomerInfo();
    }

    public subscribe(listener: (info: CustomerInfo) => void) {
        this.listeners.push(listener);
        listener(this.getCustomerInfo());
    }

    private notifyListeners(info: CustomerInfo) {
        this.listeners.forEach(l => l(info));
    }
}

export const revenueCat = RevenueCatService.getInstance();
