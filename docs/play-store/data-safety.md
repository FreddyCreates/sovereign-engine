# Play Console data safety answers

Answers for the Data safety form, based on what the app actually does. Re-check these if you add an analytics or crash SDK.

## Overview

| Question | Answer |
| --- | --- |
| Does your app collect or share any of the required user data types? | Yes |
| Is all of the user data collected by your app encrypted in transit? | Yes (HTTPS; cleartext is only permitted to localhost and the emulator host for development) |
| Do you provide a way for users to request that their data is deleted? | Yes (see privacy policy: delete on the configured server; uninstall removes device settings) |

## Data types

| Data type | Collected | Shared | Required or optional | Purpose |
| --- | --- | --- | --- | --- |
| Financial info > Purchase history | Collected | Shared with RevenueCat | Required | App functionality (entitlements) |
| Financial info > Other financial info (bank transactions, invoices) | Collected | Not shared by the app (stored on the user-configured server) | Optional (only when a bank is connected) | App functionality |
| App info and performance > Crash logs | Not collected by the app | | | |
| Device or other IDs | Collected (random app user ID) | Shared with RevenueCat | Required | App functionality, account management |
| Personal info | Not collected | | | |
| Location | Not collected | | | |
| Contacts | Not collected | | | |

## Security practices

- Data is encrypted in transit.
- Users can request data deletion.
- No independent security review has been performed.

## Advertising ID

The app does not use the advertising ID. Declare "No" on the Advertising ID question. `com.google.android.gms.permission.AD_ID` is not in the manifest.
