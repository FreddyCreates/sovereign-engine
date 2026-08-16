// oro_governance.mo
// ORO Governance Module for the Sovereign Chain
// Implements the TRACE · VERIFY · REMEMBER pattern for on-chain upgrades.

import Array "mo:base/Array";
import Nat "mo:base/Nat";
import Time "mo:base/Time";
import Principal "mo:base/Principal";

actor OroGovernance {

    public type ProposalId = Nat;
    
    public type Vote = {
        agent: Text; // ARCHON, VECTOR, LUMEN, FORGE
        approved: Bool;
        signature: Text;
        timestamp: Int;
    };

    public type Proposal = {
        id: ProposalId;
        proposer: Principal;
        description: Text;
        // EffectTrace records the exact state changes intended
        effectTrace: Text; 
        status: { #Active; #Passed; #Rejected; #Executed };
        votes: [Vote];
        createdAt: Int;
    };

    // GovernanceMemory
    stable var proposals: [Proposal] = [];
    stable var nextProposalId: Nat = 1;
    
    // The 4-Agent Council Threshold
    let QUORUM_REQUIRED: Nat = 3; 

    // TRACE: Propose an upgrade with a deterministic effect trace
    public func submitProposal(desc: Text, trace: Text) : async ProposalId {
        let id = nextProposalId;
        let newProposal : Proposal = {
            id = id;
            proposer = Principal.fromActor(this); // Using actor principal as mock
            description = desc;
            effectTrace = trace;
            status = #Active;
            votes = [];
            createdAt = Time.now();
        };
        
        proposals := Array.append(proposals, [newProposal]);
        nextProposalId += 1;
        return id;
    };

    // VERIFY: Council agents cast their cryptographic votes
    public func castVote(id: ProposalId, agentId: Text, approved: Bool, sig: Text) : async Bool {
        var found = false;
        var updatedProposals : [Proposal] = [];

        for (p in proposals.vals()) {
            if (p.id == id and p.status == #Active) {
                let newVote : Vote = {
                    agent = agentId;
                    approved = approved;
                    signature = sig;
                    timestamp = Time.now();
                };
                
                let updatedVotes = Array.append(p.votes, [newVote]);
                
                // Check if Quorum is met
                var yesVotes = 0;
                var noVotes = 0;
                for (v in updatedVotes.vals()) {
                    if (v.approved) { yesVotes += 1 } else { noVotes += 1 };
                };
                
                var newStatus = p.status;
                if (yesVotes >= QUORUM_REQUIRED) {
                    newStatus := #Passed;
                } else if (noVotes > 1) { // 4 agents total, 2 nos means impossible to get 3 yes
                    newStatus := #Rejected;
                };

                let updatedP : Proposal = {
                    id = p.id;
                    proposer = p.proposer;
                    description = p.description;
                    effectTrace = p.effectTrace;
                    status = newStatus;
                    votes = updatedVotes;
                    createdAt = p.createdAt;
                };
                updatedProposals := Array.append(updatedProposals, [updatedP]);
                found := true;
            } else {
                updatedProposals := Array.append(updatedProposals, [p]);
            }
        };

        if (found) {
            proposals := updatedProposals;
        };
        return found;
    };

    // REMEMBER: Query the GovernanceMemory
    public query func getProposal(id: ProposalId) : async ?Proposal {
        for (p in proposals.vals()) {
            if (p.id == id) {
                return ?p;
            }
        };
        return null;
    };

    // Execute passed proposals (Simulated)
    public func executeProposal(id: ProposalId) : async Bool {
        var success = false;
        var updatedProposals : [Proposal] = [];
        
        for (p in proposals.vals()) {
            if (p.id == id and p.status == #Passed) {
                let updatedP : Proposal = {
                    id = p.id;
                    proposer = p.proposer;
                    description = p.description;
                    effectTrace = p.effectTrace;
                    status = #Executed;
                    votes = p.votes;
                    createdAt = p.createdAt;
                };
                updatedProposals := Array.append(updatedProposals, [updatedP]);
                success := true;
            } else {
                updatedProposals := Array.append(updatedProposals, [p]);
            }
        };
        
        if (success) {
            proposals := updatedProposals;
        };
        return success;
    };
}
