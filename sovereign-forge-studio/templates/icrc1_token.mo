// ── SOVEREIGN OS PRODUCTION CANISTER TEMPLATE ──
// Module: ICRC-1 Compliant Crypto Token Ledger in Motoko
// Integration Protocol: [AURUM-φ-Compounding] / [VOXIS-SL-0]

import Array "mo:base/Array";
import HashMap "mo:base/HashMap";
import Principal "mo:base/Principal";
import Hash "mo:base/Hash";
import Result "mo:base/Result";
import Time "mo:base/Time";

actor class ICRC1Token(
  _name: Text,
  _symbol: Text,
  _decimals: Nat8,
  _totalSupply: Nat,
  _fee: Nat,
  _owner: Principal
) {

  // ── Types and Standard Structs ───────────────────────────────────────────
  
  public type Subaccount = [Nat8]; // 32 byte array representation
  
  public type Account = {
    owner: Principal;
    subaccount: ?Subaccount;
  };

  public type TransferArgs = {
    from_subaccount: ?Subaccount;
    to: Account;
    amount: Nat;
    fee: ?Nat;
    memo: ?[Nat8];
    created_at_time: ?u64;
  };

  public type TransferError = {
    #BadFee: { expected_fee: Nat };
    #BadBurn: { min_burn_amount: Nat };
    #InsufficientFunds: { balance: Nat };
    #TooOld;
    #CreatedInFuture: { ledger_time: u64 };
    #DuplicateOf: { duplicate_of: Nat };
    #TemporarilyUnavailable;
    #GenericError: { error_code: Nat; message: Text };
  };

  public type Value = {
    #Nat: Nat;
    #Int: Int;
    #Text: Text;
    #Blob: [Nat8];
  };

  public type MetadataRecord = {
    key: Text;
    value: Value;
  };

  // ── Stable State Mapping ──────────────────────────────────────────────────
  
  // Stable tracking array to persist user balances across upgrade cycles
  private stable var balancesArray : [(Account, Nat)] = [];
  
  // Active in-memory balance registry
  private var balances = HashMap.HashMap<Account, Nat>(accountEq, accountHash);

  // Core Ledger Constants
  private stable var tokenName : Text = _name;
  private stable var tokenSymbol : Text = _symbol;
  private stable var tokenDecimals : Nat8 = _decimals;
  private stable var totalMinted : Nat = _totalSupply;
  private stable var transactionFee : Nat = _fee;
  private stable var minterAccount : Account = { owner = _owner; subaccount = null };

  // ── Upgrade Lifecycles ────────────────────────────────────────────────────
  
  system func postupgrade() {
    balances := HashMap.fromIter<Account, Nat>(balancesArray.vals(), accountEq, accountHash);
  };

  system func preupgrade() {
    balancesArray := Array.fromIter<(Account, Nat)>(balances.entries());
  };

  // ── Ledger Bootstrapper ───────────────────────────────────────────────────
  
  private func initializeLedger() {
    let initialAccount : Account = { owner = _owner; subaccount = null };
    balances.put(initialAccount, totalMinted);
  };

  initializeLedger();

  // ── ICRC-1 Standard Queries ──────────────────────────────────────────────
  
  public query func icrc1_name() : async Text { return tokenName; };
  public query func icrc1_symbol() : async Text { return tokenSymbol; };
  public query func icrc1_decimals() : async Nat8 { return tokenDecimals; };
  public query func icrc1_total_supply() : async Nat { return totalMinted; };
  public query func icrc1_fee() : async Nat { return transactionFee; };
  public query func icrc1_minting_account() : async ?Account { return ?minterAccount; };
  
  public query func icrc1_metadata() : async [MetadataRecord] {
    return [
      { key = "icrc1:name"; value = #Text(tokenName) },
      { key = "icrc1:symbol"; value = #Text(tokenSymbol) },
      { key = "icrc1:decimals"; value = #Nat(Nat.fromNat8(tokenDecimals)) },
      { key = "icrc1:fee"; value = #Nat(transactionFee) }
    ];
  };

  public query func icrc1_balance_of(account: Account) : async Nat {
    switch (balances.get(account)) {
      case null { 0 };
      case (?bal) { bal };
    };
  };

  // ── ICRC-1 Standard Transfer Update Call ─────────────────────────────────
  
  public shared(msg) func icrc1_transfer(args: TransferArgs) : async Result.Result<Nat, TransferError> {
    let sender : Account = { owner = msg.caller; subaccount = args.from_subaccount };
    
    // 1. Fee validation
    let fee = switch (args.fee) {
      case (?f) { f };
      case null { transactionFee };
    };

    if (fee != transactionFee) {
      return #err(#BadFee({ expected_fee = transactionFee }));
    };

    // 2. Validate balances
    let senderBal = switch (balances.get(sender)) {
      case null { 0 };
      case (?bal) { bal };
    };

    let totalDeduction = args.amount + fee;
    if (senderBal < totalDeduction) {
      return #err(#InsufficientFunds({ balance = senderBal }));
    };

    // 3. Prevent self-transfers (redundant state calculations)
    if (accountEq(sender, args.to)) {
      return #err(#GenericError({ error_code = 101; message = "Cannot transfer tokens to identical self account." }));
    };

    // 4. Update balances
    let recipientBal = switch (balances.get(args.to)) {
      case null { 0 };
      case (?bal) { bal };
    };

    balances.put(sender, senderBal - totalDeduction);
    balances.put(args.to, recipientBal + args.amount);

    // 5. Fee burning (fees are permanently removed from total supply)
    totalMinted := totalMinted - fee;

    let transactionTimestamp = Time.now();
    return #ok(Nat.fromInt(transactionTimestamp));
  };

  // ── Admin Functions (Minting & Burning) ──────────────────────────────────
  
  public shared(msg) func mint(to: Account, amount: Nat) : async Result.Result<Nat, Text> {
    if (msg.caller != minterAccount.owner) {
      return #err("Unauthorized. Only minter key owner can execute mint calls.");
    };

    let toBal = switch (balances.get(to)) {
      case null { 0 };
      case (?bal) { bal };
    };

    balances.put(to, toBal + amount);
    totalMinted := totalMinted + amount;
    return #ok(totalMinted);
  };

  // ── Structural Helper Functions ──────────────────────────────────────────
  
  private func accountEq(a: Account, b: Account) : Bool {
    if (a.owner != b.owner) { return false; };
    switch (a.subaccount, b.subaccount) {
      case (null, null) { true };
      case (?sa, ?sb) { Array.equal<Nat8>(sa, sb, func(x, y) { x == y }) };
      case _ { false };
    };
  };

  private func accountHash(a: Account) : Hash.Hash {
    var h = Principal.toHash(a.owner);
    switch (a.subaccount) {
      case null {};
      case (?sa) {
        for (x in sa.vals()) {
          h := h * 31 + x;
        };
      };
    };
    return h;
  };
}
