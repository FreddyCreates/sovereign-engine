# TEAM ONBOARDING & DEVELOPMENT GUIDE
## Sovereign Engine: AI Monetization & Next-Gen Fintech Substrate OS

Welcome to the **Sovereign Engine** team workspace! This guide is designed for **ThyFriendlyFox [RGNT]** and all contributors shipping to **RevenueCat Shipaton 2026**.

---

## 1. Quick Onboarding Overview

```
+-----------------------------------------------------------------------------------+
|                        SOVEREIGN ENGINE TEAM DEVELOPMENT SITEMAP                   |
+-----------------------------------------------------------------------------------+
  ├── android-app/                   -> Native Android Kotlin / Jetpack Compose App
  ├── sovereign_infrastructure/      -> 6 Next-Gen Fintech Cores (XFIN, AURA, etc.)
  ├── tests/                         -> 31 Unit & Integration Automated Test Cases
  ├── TECHNICAL_WHITEPAPER.md        -> Architectural Specification & Database Schemas
  └── README.md                      -> Public Open-Source Documentation & Banner Assets
```

---

## 2. Setting Up Your Local Workspace

### Step 1: Clone Repository & Create Feature Branch
```bash
git clone https://github.com/FreddyCreates/sovereign-engine.git
cd sovereign-engine

# Create your feature branch
git checkout -b feature/your-feature-name
```

### Step 2: Verify Automated Tests
Run the 31 automated tests covering all 6 Next-Gen Systems:
```bash
python -m unittest tests/test_nextgen_systems.py
```

### Step 3: Run the Master Orchestrator
```bash
python sovereign_infrastructure/nextgen_systems/nextgen_master_orchestrator.py
```

---

## 3. How to Extend the 6 Next-Gen Systems

Every system is modularized inside `sovereign_infrastructure/nextgen_systems/`:

1. **`XFIN` (`xfin_engine.py`)**: Add new currency exchange rates (`FX_RATES`) or forward hedging rules.
2. **`AURA` (`aura_engine.py`)**: Modify Bayesian risk scoring thresholds or credit underwriting rules.
3. **`PULSE` (`pulse_engine.py`)**: Adjust Kuramoto coherence weights ($R$) or Customer Center winback discount tiers.
4. **`MINT` (`mint_engine.py`)**: Update Golden Ratio bonding curves ($\phi - 1 = 0.618$) or FORMA deflationary burn rates.
5. **`GRID` (`grid_engine.py`)**: Register new Wear OS Watch complications or IoT biometric sensor telemetry streams.
6. **`NEXS` (`nexs_engine.py`)**: Add new Jetpack Compose UI code templates or UCB1 multi-armed bandit paywall parameters.

---

## 4. Git Workflow & Code Review Policy

1. **All changes must pass automated tests**: `python -m unittest tests/test_nextgen_systems.py`.
2. **Add 5 unit tests for any new system or feature**: Ensure 100% test coverage in `tests/test_nextgen_systems.py`.
3. **Commit with clean conventions**:
   - `feat: ...` for new features
   - `fix: ...` for bug fixes
   - `docs: ...` for documentation updates
4. **Push and create Pull Request**:
   ```bash
   git push origin feature/your-feature-name
   ```

---

## 5. Contact & Devpost Submission Team

- **Devpost Team Lead**: `ItsnotAIlabs`
- **Teammate**: `ThyFriendlyFox [RGNT]`
- **Devpost Submission Link**: [Devpost Team Join URL](https://devpost.com/software/1377479/joins/qBXMJCY0gbLhUd28gp042A)
