# Sovereign Books Privacy Policy

Effective date: October 1, 2026

Sovereign Books ("the app") is published by the Sovereign Engine project. This policy explains what the Android app collects, why, and how to remove it.

## What the app collects

**Account identifier.** The app generates a random, anonymous app user ID on first launch. It is sent to RevenueCat so that purchases can be restored on a new device, and to the Sovereign Books API so your approvals land in your own workspace. You can change it in Settings.

**Purchase data.** Subscriptions are processed by Google Play and managed through RevenueCat. The app receives entitlement status (whether Pro is active and until when). The app never sees your payment card.

**Financial data you connect.** When you connect a bank through the Sovereign Books API, transaction data is stored on the server you configure in Settings. By default the app points at a server you run yourself. The app shows this data and sends back your decisions (confirmed categories, approved claim files, approved invoice follow-ups).

**Device settings.** The API base URL, your app user ID, and a demo-mode flag are stored locally on the device and excluded from Android backups.

## What the app does not collect

No advertising identifiers, no location, no contacts, no analytics SDKs, no crash reporting beyond what Google Play provides by default.

## Third parties

- **RevenueCat** (purchase management): [privacy policy](https://www.revenuecat.com/privacy)
- **Google Play Billing** (payments): [Google privacy policy](https://policies.google.com/privacy)
- **Plaid** (bank connection, only when the server operator enables it): [privacy policy](https://plaid.com/legal/#end-user-privacy-policy)

## Data retention and deletion

Financial data lives on the Sovereign Books server you configure. Delete it by removing the business from that server or deleting the SQLite database. Local device settings are deleted when you uninstall the app. To remove your RevenueCat customer record, contact support with your app user ID.

## Children

The app is a business bookkeeping tool and is not directed at children under 13.

## Contact

Open an issue at https://github.com/ThyFriendlyFox/sovereign-engine/issues or email the address listed on the Play Store listing.
