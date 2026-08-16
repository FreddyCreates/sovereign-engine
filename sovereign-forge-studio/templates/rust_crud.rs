// ── SOVEREIGN OS PRODUCTION CANISTER TEMPLATE ──
// Module: Rust CRUD Canister using CDK Traits
// Integration Protocol: [MCGR E1-E15] / [VOXIS-SL-0]

use candid::{CandidType, Deserialize, Principal};
use std::cell::RefCell;
use std::collections::BTreeMap;
use ic_cdk::api::time;
use ic_cdk_macros::*;

// ── Type Definitions ──────────────────────────────────────────────────────

#[derive(CandidType, Deserialize, Clone)]
pub struct Entry {
    pub id: String,
    pub title: String,
    pub content: String,
    pub timestamp: u64,
    pub author: Principal,
    pub last_modified: u64,
    pub version: u64,
}

#[derive(CandidType, Deserialize, Debug)]
pub enum CrudError {
    NotFound(String),
    AlreadyExists(String),
    Unauthorized(String),
    InvalidInput(String),
}

// ── Thread-Local State ────────────────────────────────────────────────────

thread_local! {
    // In-memory working database maps IDs to Entries
    static ENTRIES: RefCell<BTreeMap<String, Entry>> = RefCell::new(BTreeMap::new());
    
    // Sovereign OS Immutable Doctrine block [VOXIS]
    static DOCTRINE_BLOCK: RefCell<String> = RefCell::new(String::from("Creator: Medina Tech · Dallas · Dallas ISD Pilot"));
    
    // Canister Administrator
    static ADMIN: RefCell<Principal> = RefCell::new(Principal::anonymous());
}

// ── Upgrade Lifecycles (Stable Storage Serialization) ────────────────────

#[pre_upgrade]
fn pre_upgrade_hook() {
    // Serialize state BTreeMap into stable memory before upgrade
    ENTRIES.with(|entries| {
        let entries_ref = entries.borrow();
        let entries_vec: Vec<(String, Entry)> = entries_ref.iter().map(|(k, v)| (k.clone(), v.clone())).collect();
        ic_cdk::storage::stable_save((entries_vec,)).expect("Failed to write state into stable storage.");
    });
}

#[post_upgrade]
fn post_upgrade_hook() {
    // Deserialize state vectors from stable storage back to memory maps
    let (entries_vec,): (Vec<(String, Entry)>,) = ic_cdk::storage::stable_restore().expect("Failed to restore state from stable storage.");
    ENTRIES.with(|entries| {
        let mut entries_mut = entries.borrow_mut();
        for (k, v) in entries_vec {
            entries_mut.insert(k, v);
        }
    });
}

// ── Admin & Security Guards ───────────────────────────────────────────────

#[init]
fn init_canister() {
    ADMIN.with(|admin| {
        *admin.borrow_mut() = ic_cdk::caller();
    });
}

fn is_authorized(author: Principal, caller: Principal) -> bool {
    let admin_user = ADMIN.with(|a| *a.borrow());
    if caller == admin_user {
        return true;
    }
    if caller == author {
        return true;
    }
    false
}

// ── Public CRUD Query / Update API ────────────────────────────────────────

#[ic_cdk::query]
fn get_doctrine() -> String {
    DOCTRINE_BLOCK.with(|d| d.borrow().clone())
}

#[ic_cdk::update]
fn create_entry(id: String, title: String, content: String) -> Result<String, CrudError> {
    if id.is_empty() {
        return Err(CrudError::InvalidInput("Entry ID cannot be empty.".to_string()));
    }
    if title.is_empty() {
        return Err(CrudError::InvalidInput("Entry Title cannot be empty.".to_string()));
    }

    let caller = ic_cdk::caller();

    ENTRIES.with(|entries| {
        let mut map = entries.borrow_mut();
        if map.contains_key(&id) {
            return Err(CrudError::AlreadyExists(format!("Entry ID: {} already exists.", id)));
        }

        let current_time = time();
        let entry = Entry {
            id: id.clone(),
            title,
            content,
            timestamp: current_time,
            author: caller,
            last_modified: current_time,
            version: 1,
        };

        map.insert(id.clone(), entry);
        Ok(id)
    })
}

#[ic_cdk::query]
fn read_entry(id: String) -> Result<Entry, CrudError> {
    ENTRIES.with(|entries| {
        entries
            .borrow()
            .get(&id)
            .cloned()
            .ok_or_else(|| CrudError::NotFound(format!("Entry ID: {} was not found.", id)))
    })
}

#[ic_cdk::update]
fn update_entry(id: String, title: String, content: String) -> Result<bool, CrudError> {
    let caller = ic_cdk::caller();

    ENTRIES.with(|entries| {
        let mut map = entries.borrow_mut();
        if let Some(entry) = map.get_mut(&id) {
            if !is_authorized(entry.author, caller) {
                return Err(CrudError::Unauthorized("ARCHON Guard: Sender is not authorized to edit this record.".to_string()));
            }

            entry.title = title;
            entry.content = content;
            entry.last_modified = time();
            entry.version += 1;
            Ok(true)
        } else {
            Err(CrudError::NotFound(format!("Entry ID: {} was not found.", id)))
        }
    })
}

#[ic_cdk::update]
fn delete_entry(id: String) -> Result<bool, CrudError> {
    let caller = ic_cdk::caller();

    ENTRIES.with(|entries| {
        let mut map = entries.borrow_mut();
        if let Some(entry) = map.get(&id) {
            if !is_authorized(entry.author, caller) {
                return Err(CrudError::Unauthorized("ARCHON Guard: Sender is not authorized to delete this record.".to_string()));
            }
            map.remove(&id);
            Ok(true)
        } else {
            Err(CrudError::NotFound(format!("Entry ID: {} was not found.", id)))
        }
    })
}

// ── Database Utilities & Search Queries ──────────────────────────────────

#[ic_cdk::query]
fn list_entries() -> Vec<Entry> {
    ENTRIES.with(|entries| {
        entries.borrow().values().cloned().collect()
    })
}

#[ic_cdk::query]
fn search_entries(query_text: String) -> Vec<Entry> {
    let query_lower = query_text.to_lowercase();
    ENTRIES.with(|entries| {
        entries
            .borrow()
            .values()
            .filter(|entry| {
                entry.title.to_lowercase().contains(&query_lower)
                    || entry.content.to_lowercase().contains(&query_lower)
            })
            .cloned()
            .collect()
    })
}
