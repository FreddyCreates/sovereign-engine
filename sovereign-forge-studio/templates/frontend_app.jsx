// ── SOVEREIGN OS PRODUCTION FRONTEND TEMPLATE ──
// Module: React Frontend with @dfinity/agent Connection
// Integration Protocol: [MCGR E1-E15] / [VOXIS-SL-0]

import React, { useState, useEffect } from 'react';
import { Actor, HttpAgent } from '@dfinity/agent';

// ── Candid Interface Definition Factory ─────────────────────────────────────
// Auto-aligned to match the Motoko/Rust CRUD canister Candid mappings
const idlFactory = ({ IDL }) => {
  const Entry = IDL.Record({
    id: IDL.Text,
    title: IDL.Text,
    content: IDL.Text,
    timestamp: IDL.Int,
    author: IDL.Principal,
    lastModified: IDL.Int,
    version: IDL.Nat,
  });
  
  const CrudError = IDL.Variant({
    NotFound: IDL.Text,
    AlreadyExists: IDL.Text,
    Unauthorized: IDL.Text,
    InvalidInput: IDL.Text,
  });

  const CreateResult = IDL.Variant({ ok: IDL.Text, err: CrudError });
  const ReadResult = IDL.Variant({ ok: Entry, err: CrudError });
  const UpdateResult = IDL.Variant({ ok: IDL.Bool, err: CrudError });
  const DeleteResult = IDL.Variant({ ok: IDL.Bool, err: CrudError });

  return IDL.Service({
    create_entry: IDL.Func([IDL.Text, IDL.Text, IDL.Text], [CreateResult], []),
    read_entry: IDL.Func([IDL.Text], [ReadResult], ['query']),
    update_entry: IDL.Func([IDL.Text, IDL.Text, IDL.Text], [UpdateResult], []),
    delete_entry: IDL.Func([IDL.Text], [DeleteResult], []),
    list_entries: IDL.Func([], [IDL.Vec(Entry)], ['query']),
    get_doctrine: IDL.Func([], [IDL.Text], ['query']),
  });
};

export default function SovereignDashboard() {
  // ── Component State Hooks ──────────────────────────────────────────────────
  const [actor, setActor] = useState(null);
  const [doctrine, setDoctrine] = useState('Resolving system doctrine...');
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState({ text: '', type: 'info' });

  // Form Fields
  const [entryId, setEntryId] = useState('');
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');

  // ── Canister Agent Connection lifecycle ───────────────────────────────────
  useEffect(() => {
    const initializeActor = async () => {
      try {
        // Point agent to local replica (8000) or mainnet (ic0.app)
        const host = process.env.NODE_ENV === 'production' ? 'https://ic0.app' : 'http://localhost:8000';
        const agent = new HttpAgent({ host });
        
        // Local replica requires fetching root keys to verify certificate signatures
        if (process.env.NODE_ENV !== 'production') {
          await agent.fetchRootKey().catch(err => {
            console.error("Local replica signature sync failed:", err);
          });
        }
        
        // Canister ID retrieved from local project registry metadata
        const canisterId = process.env.CANISTER_ID || 'bkyz2-fmaaa-aaaaa-qaaaq-cai';
        
        const serviceActor = Actor.createActor(idlFactory, {
          agent,
          canisterId,
        });
        
        setActor(serviceActor);
      } catch (error) {
        console.error("Failed to bootstrap canister agent client:", error);
        setMessage({ text: 'Bootstrap failure: Canister connection offline.', type: 'err' });
      }
    };
    
    initializeActor();
  }, []);

  // Fetch data records when actor completes connection
  useEffect(() => {
    if (actor) {
      syncDatabase();
    }
  }, [actor]);

  // ── Database State Queries ────────────────────────────────────────────────
  const syncDatabase = async () => {
    setLoading(true);
    try {
      const doc = await actor.get_doctrine();
      setDoctrine(doc);
      
      const records = await actor.list_entries();
      // Sort by newest modified
      const sorted = [...records].sort((a, b) => Number(b.lastModified - a.lastModified));
      setEntries(sorted);
    } catch (err) {
      console.error("Query synchronization failed:", err);
      setMessage({ text: 'Sync Error: Failed to retrieve data from canister.', type: 'err' });
    } finally {
      setLoading(false);
    }
  };

  // ── Write Transactions ────────────────────────────────────────────────────
  const handleCreate = async (e) => {
    e.preventDefault();
    if (!actor || submitting) return;
    
    setSubmitting(true);
    setMessage({ text: 'Sending create transaction to blockchain...', type: 'info' });
    
    try {
      const res = await actor.create_entry(entryId, title, content);
      if ('ok' in res) {
        setMessage({ text: `Entry successfully committed: ${res.ok}`, type: 'success' });
        // Clear fields
        setEntryId('');
        setTitle('');
        setContent('');
        syncDatabase();
      } else {
        const errorKey = Object.keys(res.err)[0];
        const errorMsg = res.err[errorKey];
        setMessage({ text: `Commit Rejected: [${errorKey}] ${errorMsg}`, type: 'err' });
      }
    } catch (err) {
      console.error(err);
      setMessage({ text: 'Transaction failed. Subnet error.', type: 'err' });
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id) => {
    if (!actor || submitting) return;
    if (!window.confirm("Are you sure you want to delete this entry from blockchain?")) return;

    setSubmitting(true);
    setMessage({ text: 'Broadcasting deletion transaction...', type: 'info' });

    try {
      const res = await actor.delete_entry(id);
      if ('ok' in res) {
        setMessage({ text: 'Entry removed successfully.', type: 'success' });
        syncDatabase();
      } else {
        const errorKey = Object.keys(res.err)[0];
        setMessage({ text: `Deletion Rejected: ${res.err[errorKey]}`, type: 'err' });
      }
    } catch (err) {
      console.error(err);
      setMessage({ text: 'Transaction failed.', type: 'err' });
    } finally {
      setSubmitting(false);
    }
  };

  // ── Layout Render ─────────────────────────────────────────────────────────
  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <div style={styles.brand}>
          <div style={styles.logo}>M</div>
          <div>
            <h1 style={styles.title}>Sovereign SaaS Dashboard</h1>
            <small style={styles.doctrine}>{doctrine}</small>
          </div>
        </div>
      </header>

      {message.text && (
        <div style={{ ...styles.alert, ...styles[message.type] }}>
          {message.text}
        </div>
      )}

      <main style={styles.mainGrid}>
        
        {/* Left pane: Creator Form */}
        <section style={styles.card}>
          <h2 style={styles.sectionTitle}>Add New State Record</h2>
          <form onSubmit={handleCreate} style={styles.form}>
            <div style={styles.inputGroup}>
              <label>Record Identifier</label>
              <input style={styles.input} placeholder="e.g. entry-123" value={entryId} onChange={e => setEntryId(e.target.value)} required />
            </div>
            <div style={styles.inputGroup}>
              <label>Title</label>
              <input style={styles.input} placeholder="Enter record title" value={title} onChange={e => setTitle(e.target.value)} required />
            </div>
            <div style={styles.inputGroup}>
              <label>Content Payload</label>
              <textarea style={{...styles.input, height: '100px'}} placeholder="Write content text..." value={content} onChange={e => setContent(e.target.value)} required />
            </div>
            <button type="submit" disabled={submitting} style={styles.btnPrimary}>
              {submitting ? 'Broadcasting...' : 'Commit to Subnet'}
            </button>
          </form>
        </section>

        {/* Right pane: Database items */}
        <section style={styles.listContainer}>
          <div style={styles.listHeader}>
            <h2 style={styles.sectionTitle}>Canister Datastore Records</h2>
            <button onClick={syncDatabase} style={styles.btnSecondary} disabled={loading}>
              {loading ? 'Refreshing...' : 'Sync State'}
            </button>
          </div>

          {loading ? (
            <div style={styles.infoText}>Querying stable memory allocations...</div>
          ) : entries.length === 0 ? (
            <div style={styles.infoText}>Zero records found. Create an entry to commit state.</div>
          ) : (
            <div style={styles.grid}>
              {entries.map(entry => (
                <div key={entry.id} style={styles.recordCard}>
                  <div style={styles.cardHeader}>
                    <h3 style={styles.cardTitle}>{entry.title}</h3>
                    <span style={styles.versionBadge}>v{entry.version.toString()}</span>
                  </div>
                  <code style={styles.idCode}>ID: {entry.id}</code>
                  <p style={styles.cardBody}>{entry.content}</p>
                  <div style={styles.cardFooter}>
                    <small>Author: {entry.author.toText().substring(0, 15)}...</small>
                    <button onClick={() => handleDelete(entry.id)} style={styles.btnDanger}>Delete</button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

      </main>
    </div>
  );
}

// ── Inlined Glassmorphic Styling Sheet ──────────────────────────────────────
const styles = {
  container: { padding: '30px', fontFamily: 'system-ui, sans-serif', color: '#e2ecf5', background: '#0c0d12', minHeight: '100vh' },
  header: { borderBottom: '1px solid rgba(123, 97, 255, 0.2)', paddingBottom: '16px', marginBottom: '24px' },
  brand: { display: 'flex', alignItems: 'center', gap: '14px' },
  logo: { width: '38px', height: '38px', background: '#7b61ff', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', fontSize: '18px', color: '#fff' },
  title: { fontSize: '20px', fontWeight: '600', margin: 0 },
  doctrine: { fontSize: '11px', color: '#9ba8b8' },
  mainGrid: { display: 'grid', gridTemplateColumns: '1fr 2.2fr', gap: '30px', alignItems: 'start' },
  card: { background: '#12131a', border: '1px solid #222533', padding: '20px', borderRadius: '12px' },
  sectionTitle: { fontSize: '14px', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#fff', marginBottom: '16px' },
  form: { display: 'flex', flexDirection: 'column', gap: '16px' },
  inputGroup: { display: 'flex', flexDirection: 'column', gap: '6px' },
  input: { background: '#161822', border: '1px solid #222533', borderRadius: '8px', color: '#fff', padding: '10px', fontSize: '13px', outline: 'none' },
  btnPrimary: { background: '#7b61ff', border: 'none', color: '#fff', padding: '12px', borderRadius: '8px', cursor: 'pointer', fontWeight: '600', fontSize: '13px' },
  btnSecondary: { background: '#1e202e', border: '1px solid #222533', color: '#fff', padding: '8px 14px', borderRadius: '6px', cursor: 'pointer', fontSize: '12px' },
  btnDanger: { background: 'rgba(255, 77, 109, 0.1)', border: '1px solid #ff4d6d', color: '#ff4d6d', padding: '4px 8px', borderRadius: '4px', cursor: 'pointer', fontSize: '11px' },
  listContainer: { display: 'flex', flexDirection: 'column', gap: '16px' },
  listHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
  infoText: { color: '#525f7a', fontSize: '13px', textAlign: 'center', padding: '40px' },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: '18px' },
  recordCard: { background: '#161822', border: '1px solid #222533', padding: '16px', borderRadius: '10px', display: 'flex', flexDirection: 'column', gap: '8px' },
  cardHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center' },
  cardTitle: { fontSize: '15px', fontWeight: '600', color: '#fff', margin: 0 },
  versionBadge: { fontSize: '9px', background: 'rgba(0, 229, 160, 0.1)', border: '1px solid #00e5a0', color: '#00e5a0', padding: '1px 5px', borderRadius: '3px' },
  idCode: { fontFamily: 'monospace', fontSize: '10px', color: '#0dcaf0' },
  cardBody: { fontSize: '12.5px', color: '#9ba8b8', margin: '4px 0 10px 0', lineHeight: 1.4 },
  cardFooter: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid rgba(255,255,255,0.03)', paddingTop: '10px' },
  alert: { padding: '12px 16px', borderRadius: '8px', fontSize: '13px', marginBottom: '20px' },
  info: { background: 'rgba(123, 97, 255, 0.1)', border: '1px solid rgba(123, 97, 255, 0.3)', color: '#a496ff' },
  success: { background: 'rgba(0, 229, 160, 0.1)', border: '1px solid rgba(0, 229, 160, 0.3)', color: '#00e5a0' },
  err: { background: 'rgba(255, 77, 109, 0.1)', border: '1px solid rgba(255, 77, 109, 0.3)', color: '#ff4d6d' }
};
