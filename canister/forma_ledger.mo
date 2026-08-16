// forma_ledger.mo — Sovereign Chain Native Token Ledger
//
// Token: FORMA
// Supply: 1,000,000,000 FORMA at Genesis
// Mechanics: φ-compounding yields for staked balances, integrated with Sovereign Cycle.

import HashMap "mo:base/HashMap";
import Principal "mo:base/Principal";
import Result "mo:base/Result";
import Time "mo:base/Time";
import Float "mo:base/Float";

actor FormaLedger {

    // φ (Golden Ratio)
    let PHI : Float = 1.618033988749895;

    // Total initial supply: 1B FORMA (8 decimals)
    var totalSupply : Nat = 100_000_000_000_000_000;
    
    // Decimals
    let decimals : Nat = 8;
    let ONE_FORMA : Nat = 100_000_000;

    // Accounts mapping: Principal -> Balance
    let balances = HashMap.HashMap<Principal, Nat>(10, Principal.equal, Principal.hash);
    
    // Staked accounts mapping: Principal -> (Staked Amount, Timestamp of Stake)
    let stakedBalances = HashMap.HashMap<Principal, (Nat, Int)>(10, Principal.equal, Principal.hash);

    // Initialise genesis accounts based on genesis.json allocations
    public shared({ caller }) func initializeGenesis() : async () {
        // Only allow initialization once, typically by the network orchestrator (ARCHON)
        // Parallax Liquidity Pool (40%)
        // ORO Governance (20%)
        // Ecosystem (20%)
        // Validator Reserves (20%)
        // In this implementation, we mint it to the caller for testing.
        balances.put(caller, totalSupply);
    };

    // Standard transfer
    public shared({ caller }) func transfer(to: Principal, amount: Nat) : async Result.Result<(), Text> {
        let currentBalance = Option.get(balances.get(caller), 0);
        if (currentBalance < amount) {
            return #err("Insufficient FORMA balance");
        };

        balances.put(caller, currentBalance - amount);
        let receiverBalance = Option.get(balances.get(to), 0);
        balances.put(to, receiverBalance + amount);

        return #ok(());
    };

    // Get liquid balance
    public query func balance(of: Principal) : async Nat {
        Option.get(balances.get(of), 0);
    };

    // Stake FORMA into the Parallax Sovereign Ring
    public shared({ caller }) func stake(amount: Nat) : async Result.Result<(), Text> {
        let currentBalance = Option.get(balances.get(caller), 0);
        if (currentBalance < amount) {
            return #err("Insufficient FORMA to stake");
        };

        balances.put(caller, currentBalance - amount);
        
        let now = Time.now();
        let (existingStake, _) = Option.get(stakedBalances.get(caller), (0, now));
        stakedBalances.put(caller, (existingStake + amount, now));

        return #ok(());
    };

    // Calculate φ-compounding yield (simplified for Motoko Float math)
    // Yield = Stake * (PHI * (time_elapsed / 1_year))
    private func calculatePhiYield(amount: Nat, timestamp: Int) : Nat {
        let now = Time.now();
        let elapsedNanos = now - timestamp;
        let elapsedYears : Float = Float.fromInt(elapsedNanos) / 31_536_000_000_000_000.0;
        
        let amountFloat : Float = Float.fromInt(amount);
        // φ - 1 = 0.618 (The growth rate)
        let growthRate = PHI - 1.0;
        
        let yieldFloat = amountFloat * (growthRate * elapsedYears);
        return Float.toInt(yieldFloat);
    };

    // Unstake FORMA and claim φ-compounding yields
    public shared({ caller }) func unstake(amount: Nat) : async Result.Result<(), Text> {
        switch (stakedBalances.get(caller)) {
            case null { return #err("No staked FORMA"); };
            case (? (stakedAmount, timestamp)) {
                if (stakedAmount < amount) {
                    return #err("Cannot unstake more than currently staked");
                };

                let yield = calculatePhiYield(stakedAmount, timestamp); // simplified: yield on full amount
                
                // Update staking record
                if (stakedAmount == amount) {
                    stakedBalances.delete(caller);
                } else {
                    // Reset timestamp for remaining stake
                    stakedBalances.put(caller, (stakedAmount - amount, Time.now()));
                };

                // Add original amount + yield back to liquid balance
                let currentBalance = Option.get(balances.get(caller), 0);
                balances.put(caller, currentBalance + amount + yield);

                // Mint new tokens for yield
                totalSupply += yield;

                return #ok(());
            };
        };
    };
    
    // View staked balance and current pending yield
    public query func getStakeInfo(of: Principal) : async (Nat, Nat) {
        switch (stakedBalances.get(of)) {
            case null { return (0, 0); };
            case (? (stakedAmount, timestamp)) {
                let yield = calculatePhiYield(stakedAmount, timestamp);
                return (stakedAmount, yield);
            };
        };
    };
}
