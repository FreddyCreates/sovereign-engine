// blockchain.rs — Parallax Sovereign Chain Data Structures
//
// Defines the core blockchain types: Block, Transaction, and State transition
// mechanisms utilizing the Sovereign Cycle (873ms) and Fibonacci Kernel.

use crate::crypto;
use crate::sovereign_cycle::{FibonacciKernel, HEARTBEAT_MS};
use serde::{Serialize, Deserialize};

/// A transaction on the Sovereign Chain.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Transaction {
    pub tx_id: [u8; 32],
    pub sender: String, // Ed25519 public key encoded
    pub receiver: String,
    pub amount: f64,
    pub fee: f64,
    pub signature: [u8; 64],
    pub timestamp_ms: u64,
}

impl Transaction {
    pub fn new(sender: String, receiver: String, amount: f64, fee: f64, timestamp_ms: u64) -> Self {
        // Dummy transaction ID generation (replace with proper hashing in production)
        let tx_id = [0u8; 32];
        Self {
            tx_id,
            sender,
            receiver,
            amount,
            fee,
            signature: [0u8; 64], // To be signed
            timestamp_ms,
        }
    }
}

/// A block generated at φ-harmonic intervals (873ms).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Block {
    pub beat: u64,
    pub parent_hash: [u8; 32],
    pub hash: [u8; 32],
    pub transactions: Vec<Transaction>,
    pub proposer: String, // Validator AGI (e.g., COGNOVEX)
    pub kernel_seal: [u8; 32], // Fibonacci kernel compression seal
    pub timestamp_ms: u64,
}

impl Block {
    pub fn new(beat: u64, parent_hash: [u8; 32], transactions: Vec<Transaction>, proposer: String, kernel_seal: [u8; 32]) -> Self {
        let timestamp_ms = beat * HEARTBEAT_MS;
        let mut block = Self {
            beat,
            parent_hash,
            hash: [0u8; 32],
            transactions,
            proposer,
            kernel_seal,
            timestamp_ms,
        };
        block.hash = block.compute_hash();
        block
    }

    /// Computes the BLAKE3 hash of the block contents.
    pub fn compute_hash(&self) -> [u8; 32] {
        // In a real implementation, serialize block headers and hash.
        let mut combined = Vec::new();
        combined.extend_from_slice(&self.parent_hash);
        combined.extend_from_slice(&self.beat.to_be_bytes());
        combined.extend_from_slice(&self.kernel_seal);
        *blake3::hash(&combined).as_bytes()
    }
}
