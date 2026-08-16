// risk_policy.ts — Parallax Risk Gate
//
// Ensures orders meet margin and systemic risk requirements before hitting the matching engine.

import { Order } from './matching_engine.js';
import { Clearinghouse } from './clearinghouse.js';

export class RiskPolicyGate {
    constructor(private clearinghouse: Clearinghouse) {}

    public validateOrder(order: Order): boolean {
        // Market format expected: "BASE-QUOTE" (e.g. "FORMA-USDC")
        const [base, quote] = order.market.split('-');

        if (order.side === 'BUY') {
            // Check if user has enough quote asset to cover (price * amount)
            const requiredQuote = order.price * order.amount;
            const availableQuote = this.clearinghouse.getBalance(order.traderId, quote);
            if (availableQuote < requiredQuote) return false;
        } else {
            // Check if user has enough base asset to cover (amount)
            const requiredBase = order.amount;
            const availableBase = this.clearinghouse.getBalance(order.traderId, base);
            if (availableBase < requiredBase) return false;
        }

        return true;
    }
}
