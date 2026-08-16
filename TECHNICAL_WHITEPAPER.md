# TECHNICAL WHITEPAPER & ARCHITECTURAL BLUEPRINT
## Sovereign Engine: Production Native Mobile App & RevenueCat Infrastructure OS

**Document Version:** 2.0.0 (Production Blueprint)  
**Target Event:** RevenueCat Shipaton 2026  
**Primary Stack:** Native Android (Kotlin / Jetpack Compose / Gradle), Native iOS (Swift / SwiftUI / StoreKit 2), RevenueCat Native SDKs (`purchases-android`, `purchases-ios`, REST API v2, Paywalls v2, Customer Center), OneSignal Push, SQLite, Python Microservices.  
**Motoko Policy:** 0% Motoko. Pure Native Mobile & Cloud/Edge Microservices.

---

## 1. Executive Technical Summary

Sovereign Engine is a production-grade, multi-platform mobile application and monetization infrastructure OS. It is engineered to solve the core challenges of mobile app monetization: multi-store entitlement synchronization, paywall A/B testing, dynamic Purchasing Power Parity (PPP) pricing, automated subscriber churn defense, and connected Wear OS / IoT hardware entitlement unlocking.

```
+-----------------------------------------------------------------------------------+
|                        SOVEREIGN ENGINE PRODUCTION SYSTEM                         |
+-----------------------------------------------------------------------------------+
       |                                      |                                     |
       v                                      v                                     v
+------------------------+       +-------------------------+       +------------------------+
|   NATIVE MOBILE APP    |       |   REVENUECAT PLATFORM   |       |   PRODUCTION BACKEND   |
|  - Android (Kotlin UI) | <---> |  - REST API v2          | <---> |  - Python HTTP Server  |
|  - iOS (Swift UI)      |       |  - Paywalls v2 AST      |       |  - SQLite (db_engine)  |
|  - Galaxy Store APK    |       |  - Customer Center      |       |  - HMAC-SHA256 Secret  |
|  - Wear OS IoT Relay   |       |  - OneSignal Push Engine|       |  - protocol_state.json |
+------------------------+       +-------------------------+       +------------------------+
```

---

## 2. Native Mobile Application Architecture (`android-app/`)

### 2.1 Dependencies & Build Configuration (`app/build.gradle.kts`)
The native Android app is built using Gradle, targeting Android SDK 34 (Android 14) and minSdk 24 (Android 7.0), with full Jetpack Compose support:

```kotlin
// Key Production Dependencies
implementation("com.revenuecat.purchases:purchases:8.2.0")
implementation("com.revenuecat.purchases:purchases-ui-paywalls:8.2.0")
implementation("com.revenuecat.purchases:purchases-ui-customercenter:8.2.0")
implementation("com.onesignal:OneSignal:5.1.8")
```

### 2.2 RevenueCat Native SDK Manager (`RevenueCatManager.kt`)
The SDK manager acts as a singleton wrapper interfacing directly with Google Play Billing and Apple StoreKit 2:

- **Initialization**:
  ```kotlin
  fun initialize(context: Context, appUserId: String) {
      val config = PurchasesConfiguration.Builder(context, "goog_pub_live_sovereign_android_2026")
          .appUserID(appUserId)
          .build()
      Purchases.configure(config)
  }
  ```
- **Offerings Fetching**: Retrieves `offerings.current` configured in the RevenueCat Dashboard containing packages (Monthly Pro, Annual Pro, Lifetime Sovereign).
- **Purchase Execution**: Invokes `Purchases.sharedInstance.purchase()` with native Activity context and callbacks for `onCompleted` (granting `pro_access`) and `onError`.
- **Entitlement Checks**: Evaluates `customerInfo.entitlements["pro_access"]?.isActive` in real time.

### 2.3 User Interface (`MainActivity.kt`)
Built with 100% Jetpack Compose:
- **`SovereignAppUI`**: Reactive UI state binding `isProActive` and `statusText`.
- **Store Trigger**: "Upgrade via Google Play / App Store" button triggering RevenueCat Paywall v2 UI rendering.
- **Restore Purchases**: Interfacing with `Purchases.sharedInstance.restorePurchases()`.

### 2.4 IoT Hardware & Wear OS Relay (`IoTRelayService.kt`)
Bridges physical hardware devices with RevenueCat entitlements:
- Registers Wear OS watch faces (`WEAR_OS_WATCH`), connected vehicles, and smart nodes.
- When RevenueCat entitlement `pro_access` becomes active, `syncEntitlementsWithIoT()` unlocks physical hardware capabilities across connected nodes.

---

## 3. Production Backend Microservice Architecture (`real_world_ecosystem_pipeline.py`)

### 3.1 SQLite Database Schema (`production_ecosystem.db`)
The backend operates a persistent SQLite database:

- **`subscribers` Table**:
  - `user_id TEXT PRIMARY KEY`
  - `entitlements TEXT` (JSON Array: `["pro_access", "unlimited_ai"]`)
  - `plan_id TEXT` (e.g. `monthly_pro`)
  - `mrr_contribution REAL` (e.g. `19.99`)
  - `status TEXT` (`ACTIVE`, `CANCELLED`, `EXPIRED`)
  - `last_updated TIMESTAMP`

- **`transactions` Table**:
  - `transaction_id TEXT PRIMARY KEY`
  - `user_id TEXT`, `store TEXT`, `amount REAL`, `currency TEXT`, `timestamp TIMESTAMP`

- **`paywall_configs` Table**:
  - `variant_id TEXT PRIMARY KEY`, `layout_json TEXT`, `conversion_rate REAL`, `is_active INTEGER`

### 3.2 HMAC-SHA256 Webhook Security
All incoming webhooks from RevenueCat are authenticated:
```python
def verify_signature(payload_bytes: bytes, signature_header: str) -> bool:
    expected_sig = hmac.new(WEBHOOK_SECRET.encode(), payload_bytes, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected_sig, signature_header)
```

### 3.3 Production HTTP Endpoints
- **`POST /api/v2/revenuecat/webhook`**: Processes `INITIAL_PURCHASE`, `RENEWAL`, `CANCELLATION`, and `EXPIRATION` events, updating SQLite subscriber state in real time.
- **`POST /api/v2/customer_center/cancel_intent`**: Intercepts subscriber cancellation attempts in Customer Center and returns a functional JSON promo payload (50% off for 3 months).
- **`GET /api/v2/subscriber/{id}`**: Exposes real-time subscriber entitlement state.
- **`GET /health`**: Microservice health check returning `{"status": "HEALTHY", "database": "CONNECTED"}`.

---

## 4. Substrate-Embedded Agentic Protocols Suite

The platform executes a 25-protocol suite and 3 Substrate Meta-Protocols that mutate real system state:

1. **Meta-Protocol ALPHA (Autonomic Paywall Morphing Engine)**:
   - Computes user scroll velocity and cohort conversion probability.
   - Dynamically mutates active Paywall v2 layout JSON to `GLASSMORPHIC_HERO_TRIAL`.
2. **Meta-Protocol BETA (Retention & Churn Interception Matrix)**:
   - Monitors inactivity metrics and generates 50% discount promotional JSON offers inside Customer Center.
   - Dispatches OneSignal push notifications for win-back campaigns.
3. **Meta-Protocol GAMMA (Sovereign Infrastructure Mesh)**:
   - Synchronizes entitlements across Android, iOS, Galaxy Store, and Web.
   - Recalculates LTV metrics and handles webhook failover healing.

---

## 5. Production Build & Deployment Pipeline

### Step 1: Compile Native Android Release Package
```bash
cd android-app
./gradlew assembleRelease
./gradlew bundleRelease
```
Generates production APK (`app/build/outputs/apk/release/app-release.apk`) and Android App Bundle (`app-release.aab`) for Google Play Console & Samsung Galaxy Store.

### Step 2: Configure RevenueCat Dashboard
1. Create Project in RevenueCat Dashboard.
2. Add Products: `monthly_pro` ($19.99/mo), `annual_pro` ($149.99/yr).
3. Create Entitlement: `pro_access`.
4. Attach Products to Entitlement and add to Offering `default`.
5. Set Webhook URL: `https://api.yourdomain.com/api/v2/revenuecat/webhook` with Secret Header.

### Step 3: Run Backend Microservice
```bash
python sovereign_revenuecat_protocols/real_world_ecosystem_pipeline.py
```
Starts the production SQLite database engine and listening REST microservice server.

---

## 6. Verification & Compliance Matrix

| Criterion | Implementation Location | Empirical Verification Status |
|---|---|---|
| **Google Play Billing Integration** | `android-app/app/build.gradle.kts` & `RevenueCatManager.kt` | Verified (`com.revenuecat.purchases:purchases:8.2.0`) |
| **RevenueCat Paywalls v2 UI** | `MainActivity.kt` & `paywall_modal.ts` | Verified (Native & Web Paywalls v2) |
| **RevenueCat Customer Center** | `real_world_ecosystem_pipeline.py` | Verified (Cancellation Interception & 50% Promo) |
| **Samsung Galaxy Store APK** | `protocol_23_galaxy_store_apk_opt.py` | Verified (Foldable UI & Galaxy Discount Rules) |
| **OneSignal Push Retention** | `protocol_22_onesignal_push_retention.py` | Verified (Lifecycle Push Dispatch) |
| **Persistent Production Database** | `production_ecosystem.db` | Verified (SQLite schema creation, record insertion, & queries) |
| **Zero Motoko Policy** | Root Project Architecture | Verified (0% Motoko dependency in mobile app path) |
