// ── SOVEREIGN OS PRODUCTION CANISTER TEMPLATE ──
// Module: ICRC-1 Compliant Crypto Token Ledger in Rust
// Integration Protocol: [AURUM-φ-Compounding] / [VOXIS-SL-0]

use candid::{CandidType, Deserialize, Principal};
use std::cell::RefCell;
use std::collections::HashMap;
use ic_cdk::api::time;
use ic_cdk_macros::*;

// ── Types and Standard Structs ───────────────────────────────────────────

#[derive(CandidType, Deserialize, Clone, Hash, Eq, PartialEq, Debug)]
pub struct Account {
    pub owner: Principal,
    pub subaccount: Option<[u8; 32]>,
}

#[derive(CandidType, Deserialize, Clone)]
pub struct TransferArgs {
    pub from_subaccount: Option<[u8; 32]>,
    pub to: Account,
    pub amount: u128,
    pub fee: Option<u128>,
    pub memo: Option<Vec<u8>>,
    pub created_at_time: Option<u64>,
}

#[derive(CandidType, Deserialize, Debug)]
pub enum TransferError {
    BadFee { expected_fee: u128 },
    BadBurn { min_burn_amount: u128 },
    InsufficientFunds { balance: u128 },
    TooOld,
    CreatedInFuture { ledger_time: u64 },
    GenericError { error_code: u64, message: String },
}

#[derive(CandidType, Deserialize, Clone)]
pub enum Value {
    Nat(u128),
    Int(i128),
    Text(String),
    Blob(Vec<u8>),
}

#[derive(CandidType, Deserialize, Clone)]
pub struct MetadataRecord {
    pub key: String,
    pub value: Value,
}

// ── Thread-Local State ────────────────────────────────────────────────────

thread_local! {
    // Balances database mapping Account to token balance
    static BALANCES: RefCell<HashMap<Account, u128>> = RefCell::new(HashMap::new());
    
    // Core parameters
    static TOKEN_NAME: RefCell<String> = RefCell::new(String::from("Sovereign Aurum"));
    static TOKEN_SYMBOL: RefCell<String> = RefCell::new(String::from("AUR"));
    static TOKEN_DECIMALS: RefCell<u8> = RefCell::new(8);
    static TOTAL_SUPPLY: RefCell<u128> = RefCell::new(1_000_000_000_000_000); // 10M tokens considering decimals
    static TRANSACTION_FEE: RefCell<u128> = RefCell::new(10_000); // 0.0001 AUR fee
    
    static MINTER_OWNER: RefCell<Principal> = RefCell::new(Principal::anonymous());
}

// ── System Upgrade Lifecycles ─────────────────────────────────────────────

#[pre_upgrade]
fn pre_upgrade_hook() {
    BALANCES.with(|bal| {
        let bal_ref = bal.borrow();
        let bal_vec: Vec<(Account, u128)> = bal_ref.iter().map(|(k, v)| (k.clone(), *v)).collect();
        ic_cdk::storage::stable_save((bal_vec,)).expect("Failed to write token balance state to stable memory.");
    });
}

#[post_upgrade]
fn post_upgrade_hook() {
    let (bal_vec,): (Vec<(Account, u128)>,) = ic_cdk::storage::stable_restore().expect("Failed to read stable memory token balances.");
    BALANCES.with(|bal| {
        let mut bal_mut = bal.borrow_mut();
        for (k, v) in bal_vec {
            bal_mut.insert(k, v);
        }
    });
}

// ── Initialization Hook ───────────────────────────────────────────────────

#[init]
fn init_canister(name: String, symbol: String, decimals: u8, total_supply: u128, fee: u128, owner: Principal) {
    TOKEN_NAME.with(|n| *n.borrow_mut() = name);
    TOKEN_SYMBOL.with(|s| *s.borrow_mut() = symbol);
    TOKEN_DECIMALS.with(|d| *d.borrow_mut() = decimals);
    TOTAL_SUPPLY.with(|ts| *ts.borrow_mut() = total_supply);
    TRANSACTION_FEE.with(|f| *f.borrow_mut() = fee);
    MINTER_OWNER.with(|o| *o.borrow_mut() = owner);

    // Bootstrap initial token allocation to owner key
    let initial_account = Account {
        owner,
        subaccount: None,
    };
    BALANCES.with(|bal| {
        bal.borrow_mut().insert(initial_account, total_supply);
    });
}

// ── ICRC-1 Standard Queries ──────────────────────────────────────────────

#[ic_cdk::query]
fn icrc1_name() -> String {
    TOKEN_NAME.with(|n| n.borrow().clone())
}

#[ic_cdk::query]
fn icrc1_symbol() -> String {
    TOKEN_SYMBOL.with(|s| s.borrow().clone())
}

#[ic_cdk::query]
fn icrc1_decimals() -> u8 {
    TOKEN_DECIMALS.with(|d| *d.borrow())
}

#[ic_cdk::query]
fn icrc1_total_supply() -> u128 {
    TOTAL_SUPPLY.with(|ts| *ts.borrow())
}

#[ic_cdk::query]
fn icrc1_fee() -> u128 {
    TRANSACTION_FEE.with(|f| *f.borrow())
}

#[ic_cdk::query]
fn icrc1_minting_account() -> Option<Account> {
    let minter = MINTER_OWNER.with(|o| *o.borrow());
    Some(Account {
        owner: minter,
        subaccount: None,
    })
}

#[ic_cdk::query]
fn icrc1_balance_of(account: Account) -> u128 {
    BALANCES.with(|bal| *bal.borrow().get(&account).unwrap_or(&0))
}

#[ic_cdk::query]
fn icrc1_metadata() -> Vec<MetadataRecord> {
    vec![
        MetadataRecord {
            key: "icrc1:name".to_string(),
            value: Value::Text(icrc1_name()),
        },
        MetadataRecord {
            key: "icrc1:symbol".to_string(),
            value: Value::Text(icrc1_symbol()),
        },
        MetadataRecord {
            key: "icrc1:decimals".to_string(),
            value: Value::Nat(icrc1_decimals() as u128),
        },
        MetadataRecord {
            key: "icrc1:fee".to_string(),
            value: Value::Nat(icrc1_fee()),
        },
    ]
}

// ── ICRC-1 Standard Transfer Update Call ─────────────────────────────────

#[ic_cdk::update]
fn icrc1_transfer(args: TransferArgs) -> Result<u64, TransferError> {
    let caller = ic_cdk::caller();
    let sender = Account {
        owner: caller,
        subaccount: args.from_subaccount,
    };

    let fee = TRANSACTION_FEE.with(|f| *f.borrow());
    if let Some(arg_fee) = args.fee {
        if arg_fee != fee {
            return Err(TransferError::BadFee { expected_fee: fee });
        }
    }

    let total_deduction = args.amount + fee;

    BALANCES.with(|bal| {
        let mut map = bal.borrow_mut();
        let sender_balance = *map.get(&sender).unwrap_or(&0);

        if sender_balance < total_deduction {
            return Err(TransferError::InsufficientFunds { balance: sender_balance });
        }

        if sender == args.to {
            return Err(TransferError::GenericError {
                error_code: 101,
                message: "Self transfers are rejected by ledger configuration.".to_string(),
            });
        }

        let recipient_balance = *map.get(&args.to).unwrap_or(&0);

        // Perform balance transitions
        map.insert(sender, sender_balance - total_deduction);
        map.insert(args.to.clone(), recipient_balance + args.amount);

        // Burn transaction fee
        TOTAL_SUPPLY.with(|supply| {
            let mut s = supply.borrow_mut();
            *s -= fee;
        });

        Ok(time())
    })
}

// ── Admin Functions (Minting) ─────────────────────────────────────────────

#[ic_cdk::update]
fn mint(to: Account, amount: u128) -> Result<u128, String> {
    let caller = ic_cdk::caller();
    let minter = MINTER_OWNER.with(|o| *o.borrow());

    if caller != minter {
        return Err("Unauthorized. Only minter key owner can execute mint calls.".to_string());
    }

    BALANCES.with(|bal| {
        let mut map = bal.borrow_mut();
        let balance = *map.get(&to).unwrap_or(&0);
        map.insert(to, balance + amount);
    });

    TOTAL_SUPPLY.with(|supply| {
        let mut s = supply.borrow_mut();
        *s += amount;
        Ok(*s)
    })
}
