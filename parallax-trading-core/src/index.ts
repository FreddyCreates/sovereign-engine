// index.ts — Parallax Trading Core Entry Point
//
// Exports the Parallax matching engine, risk gate, and clearinghouse.
// Designed to be embedded within the Sovereign Node execution environment.

export * from './matching_engine.js';
export * from './clearinghouse.js';
export * from './risk_policy.js';
