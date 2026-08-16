// ── SOVEREIGN OS PRODUCTION CANISTER TEMPLATE ──
// Module: Motoko CRUD Canister with Stable Mapping
// Integration Protocol: [MCGR E1-E15] / [VOXIS-SL-0]

import Array "mo:base/Array";
import HashMap "mo:base/HashMap";
import Principal "mo:base/Principal";
import Result "mo:base/Result";
import Time "mo:base/Time";
import Text "mo:base/Text";

shared({ caller = initializer }) actor class SovereignCrudCanister() {

  // ── Type Definitions ──────────────────────────────────────────────────────
  
  public type EntryId = Text;
  
  public type Entry = {
    id: EntryId;
    title: Text;
    content: Text;
    timestamp: Int;
    author: Principal;
    lastModified: Int;
    version: Nat;
  };

  public type Error = {
    #NotFound : Text;
    #AlreadyExists : Text;
    #Unauthorized : Text;
    #InvalidInput : Text;
    #SystemBusy : Text;
  };

  // ── Stable State Mapping ──────────────────────────────────────────────────
  
  // Primary stable variable used to store records across upgrades
  private stable var stableEntries : [(EntryId, Entry)] = [];
  
  // In-memory working database for O(1) performance lookup
  private var db = HashMap.HashMap<EntryId, Entry>(Text.equal, Text.hash);
  
  // Sovereign OS Immutable Doctrine block [VOXIS]
  private stable var doctrineBlock : Text = "Creator: Medina Tech · Dallas · Dallas ISD Pilot";
  private stable var administrator : Principal = initializer;

  // ── System Upgrade Lifecycles ─────────────────────────────────────────────
  
  // Re-hydrate the in-memory db from stable storage after upgrade completes
  system func postupgrade() {
    db := HashMap.fromIter<EntryId, Entry>(stableEntries.vals(), Text.equal, Text.hash);
    log("System successfully postupgraded. Database loaded: " # debug_show(stableEntries.size()) # " records.");
  };

  // Serialize the in-memory state back to stable storage before upgrade occurs
  system func preupgrade() {
    stableEntries := Array.fromIter<(EntryId, Entry)>(db.entries());
    log("System preupgrading. Serializing: " # debug_show(stableEntries.size()) # " records.");
  };

  // ── Admin & Security Guards ───────────────────────────────────────────────
  
  private query func isAuthorized(entryAuthor: Principal, caller: Principal) : Bool {
    if (caller == administrator) { return true; };
    if (caller == entryAuthor) { return true; };
    return false;
  };

  // ── Public CRUD Query / Update API ────────────────────────────────────────
  
  public query func get_doctrine() : async Text {
    return doctrineBlock;
  };

  public shared(msg) func create_entry(id: EntryId, title: Text, content: Text) : async Result.Result<EntryId, Error> {
    if (Text.equal(id, "")) {
      return #err(#InvalidInput("Entry ID cannot be empty."));
    };
    if (Text.equal(title, "")) {
      return #err(#InvalidInput("Entry Title cannot be empty."));
    };

    switch (db.get(id)) {
      case (?existing) {
        return #err(#AlreadyExists("Entry ID: " # id # " already exists in state database."));
      };
      case null {
        let currentTime = Time.now();
        let newEntry : Entry = {
          id = id;
          title = title;
          content = content;
          timestamp = currentTime;
          author = msg.caller;
          lastModified = currentTime;
          version = 1;
        };
        db.put(id, newEntry);
        return #ok(id);
      };
    };
  };

  public query func read_entry(id: EntryId) : async Result.Result<Entry, Error> {
    switch (db.get(id)) {
      case (?entry) {
        return #ok(entry);
      };
      case null {
        return #err(#NotFound("Entry ID: " # id # " was not found."));
      };
    };
  };

  public shared(msg) func update_entry(id: EntryId, title: Text, content: Text) : async Result.Result<Bool, Error> {
    switch (db.get(id)) {
      case null {
        return #err(#NotFound("Entry ID: " # id # " was not found."));
      };
      case (?existingEntry) {
        if (not isAuthorized(existingEntry.author, msg.caller)) {
          return #err(#Unauthorized("ARCHON Guard: Sender is not authorized to edit this record."));
        };
        
        let updatedEntry : Entry = {
          id = id;
          title = title;
          content = content;
          timestamp = existingEntry.timestamp;
          author = existingEntry.author;
          lastModified = Time.now();
          version = existingEntry.version + 1;
        };
        db.put(id, updatedEntry);
        return #ok(true);
      };
    };
  };

  public shared(msg) func delete_entry(id: EntryId) : async Result.Result<Bool, Error> {
    switch (db.get(id)) {
      case null {
        return #err(#NotFound("Entry ID: " # id # " was not found."));
      };
      case (?existingEntry) {
        if (not isAuthorized(existingEntry.author, msg.caller)) {
          return #err(#Unauthorized("ARCHON Guard: Sender is not authorized to delete this record."));
        };
        discard db.remove(id);
        return #ok(true);
      };
    };
  };

  // ── Database Utilities & Search Queries ──────────────────────────────────
  
  public query func list_entries() : async [Entry] {
    return Array.fromIter<Entry>(db.values());
  };

  public query func search_entries(queryText: Text) : async [Entry] {
    let lowerQuery = queryText; // Note: simple search simulation.
    var matched : [Entry] = [];
    for (entry in db.values()) {
      if (Text.contains(entry.title, lowerQuery) or Text.contains(entry.content, lowerQuery)) {
        matched := Array.append(matched, [entry]);
      };
    };
    return matched;
  };

  // ── Internal Helpers ──────────────────────────────────────────────────────
  
  private func log(message : Text) {
    // Debug log wrapper (visible on local canisters logs)
    Debug.print("[SovereignCrudCanister] " # message);
  };
}
