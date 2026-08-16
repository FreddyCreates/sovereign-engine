// clearinghouse.ts — Parallax Settlement & Ledger
//
// Handles the net settlement of trades executed by the Matching Engine.

import { Trade } from './matching_engine.js';

export class Clearinghouse {
    // traderId -> asset -> balance
    private ledgers: Record<string, Record<string, number>> = {};

    public deposit(traderId: string, asset: string, amount: number) {
        if (!this.ledgers[traderId]) this.ledgers[traderId] = {};
        if (!this.ledgers[traderId][asset]) this.ledgers[traderId][asset] = 0;
        this.ledgers[traderId][asset] += amount;
    }

    public withdraw(traderId: string, asset: string, amount: number): boolean {
        if (!this.ledgers[traderId] || (this.ledgers[traderId][asset] || 0) < amount) {
            return false; // Insufficient balance
        }
        this.ledgers[traderId][asset] -= amount;
        return true;
    }

    public getBalance(traderId: string, asset: string): number {
        return (this.ledgers[traderId] && this.ledgers[traderId][asset]) || 0;
    }

    public settleTrades(trades: Trade[]) {
        for (const trade of trades) {
            // Market format expected: "BASE-QUOTE" (e.g. "FORMA-USDC")
            const [base, quote] = trade.market.split('-');
            const quoteAmount = trade.amount * trade.price;

            // In a real execution, we need to know who was BUY and who was SELL.
            // For simplicity in settlement phase, we assume the Clearinghouse is fed 
            // explicit ledger transfers derived from the Trade object and Side logic 
            // inside the matching engine, but here we provide the primitive transfer mechanism.
        }
    }

    public executeTransfer(fromTrader: string, toTrader: string, asset: string, amount: number): boolean {
        if (this.withdraw(fromTrader, asset, amount)) {
            this.deposit(toTrader, asset, amount);
            return true;
        }
        return false;
    }
}
