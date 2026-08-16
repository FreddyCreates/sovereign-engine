// matching_engine.ts — Parallax Order Matching Engine
//
// Native on-chain matching engine for the Sovereign Chain.
// Utilises a continuous limit order book (CLOB) optimized for the 873ms cycle.

export type OrderSide = 'BUY' | 'SELL';

export interface Order {
    id: string;
    traderId: string;
    market: string;
    side: OrderSide;
    price: number;
    amount: number;
    timestampMs: number;
}

export interface Trade {
    tradeId: string;
    makerOrderId: string;
    takerOrderId: string;
    market: string;
    price: number;
    amount: number;
    timestampMs: number;
}

export class MatchingEngine {
    // Market -> Side -> Orders (sorted by price, time)
    private orderBooks: Record<string, { bids: Order[], asks: Order[] }> = {};

    public initializeMarket(market: string) {
        if (!this.orderBooks[market]) {
            this.orderBooks[market] = { bids: [], asks: [] };
        }
    }

    public submitOrder(order: Order): Trade[] {
        this.initializeMarket(order.market);
        const book = this.orderBooks[order.market];
        const trades: Trade[] = [];

        let remainingAmount = order.amount;

        if (order.side === 'BUY') {
            while (remainingAmount > 0 && book.asks.length > 0 && book.asks[0].price <= order.price) {
                const bestAsk = book.asks[0];
                const tradeAmount = Math.min(remainingAmount, bestAsk.amount);
                
                trades.push(this.executeTrade(bestAsk, order, tradeAmount, bestAsk.price));
                
                bestAsk.amount -= tradeAmount;
                remainingAmount -= tradeAmount;

                if (bestAsk.amount === 0) {
                    book.asks.shift();
                }
            }
            if (remainingAmount > 0) {
                order.amount = remainingAmount;
                this.insertOrder(book.bids, order, 'DESC');
            }
        } else { // SELL
            while (remainingAmount > 0 && book.bids.length > 0 && book.bids[0].price >= order.price) {
                const bestBid = book.bids[0];
                const tradeAmount = Math.min(remainingAmount, bestBid.amount);
                
                trades.push(this.executeTrade(bestBid, order, tradeAmount, bestBid.price));
                
                bestBid.amount -= tradeAmount;
                remainingAmount -= tradeAmount;

                if (bestBid.amount === 0) {
                    book.bids.shift();
                }
            }
            if (remainingAmount > 0) {
                order.amount = remainingAmount;
                this.insertOrder(book.asks, order, 'ASC');
            }
        }

        return trades;
    }

    private executeTrade(maker: Order, taker: Order, amount: number, price: number): Trade {
        return {
            tradeId: `TRD-${Date.now()}-${Math.random().toString(36).substring(7)}`,
            makerOrderId: maker.id,
            takerOrderId: taker.id,
            market: maker.market,
            price,
            amount,
            timestampMs: Date.now()
        };
    }

    private insertOrder(book: Order[], order: Order, sortDirection: 'ASC' | 'DESC') {
        let i = 0;
        for (; i < book.length; i++) {
            if (sortDirection === 'ASC' && order.price < book[i].price) break;
            if (sortDirection === 'DESC' && order.price > book[i].price) break;
        }
        book.splice(i, 0, order);
    }

    public getOrderBook(market: string) {
        return this.orderBooks[market] || { bids: [], asks: [] };
    }
}
