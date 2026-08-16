// Freight Sovereign OS Governance Canister production seed.
// Final deployment should split this into the multi-canister mesh described in
// the source plan and connect it to audited storage and adapter canisters.

import Array "mo:base/Array";
import Text "mo:base/Text";

actor GovernanceCanister {
  public type ComplianceIssue = {
    code : Text;
    message : Text;
    severity : Text;
    reference : ?Text;
  };

  public type ComplianceDecision = {
    allowed : Bool;
    issues : [ComplianceIssue];
    warnings : [ComplianceIssue];
  };

  stable var charterVersion : Text = "FSOS-CPL-0.1.0";

  public query func getCharterVersion() : async Text {
    charterVersion
  };

  public query func brokerRecordFields() : async [Text] {
    [
      "shipper_name",
      "carrier_name",
      "rate",
      "commodity",
      "origin",
      "destination",
      "freight_charges",
      "payment_date",
      "non_brokerage_services"
    ]
  };

  public query func agentModeBoundary() : async Text {
    "Agent-mode deployment requires written carrier contracts, long-term relationship posture, no direct shipper negotiation by platform, and no platform handling of shipper-to-carrier funds. Counsel review required."
  };
}

