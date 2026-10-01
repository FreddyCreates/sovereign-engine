# Sovereign Books for Android

Kotlin + Jetpack Compose client for the Sovereign Books API. It renders the
approval card stack (categorize, tax credit, invoice follow-up), cash and
runway, the tax credit estimate, and a RevenueCat-powered Pro subscription.

## Layout

```
app/src/main/java/com/sovereignengine/books/
  SovereignBooksApp.kt      Application: configures RevenueCat
  MainActivity.kt           Single activity, Compose content
  billing/RevenueCatManager.kt   Offerings, purchase, restore, entitlement check
  data/BooksApi.kt          HTTP client for sovereign_dashboard_server.py
  data/BooksRepository.kt   Builds approval cards; falls back to DemoData offline
  data/AppSettings.kt       API URL, app user ID, free-plan approval counter
  ui/MainViewModel.kt       UiState and actions
  ui/SovereignApp.kt        Bottom navigation shell
  ui/screens/               Home, Approvals, Credits, Pro, Settings
```

## Build

Requirements: JDK 17+, Android SDK with platform 36 and build-tools 36.

```bash
cp local.properties.example local.properties   # fill in sdk.dir and keys
./gradlew :app:assembleDebug                    # debug APK
./gradlew :app:bundleRelease                    # Play Store bundle
```

With no `REVENUECAT_GOOGLE_API_KEY` the app builds and runs, but the Pro tab
reports that purchases are not configured. With no reachable API it shows
sample data and says so on the Home screen.

## API endpoints used

| Screen | Endpoint |
| --- | --- |
| Home | `GET /api/v1/books/home`, `GET /api/v1/books/runway` |
| Approvals | `GET /api/v1/books/inbox`, `POST /api/v1/books/transactions/confirm`, `GET /api/v1/books/invoices` |
| Credits | `GET /api/v1/agentic_qb/tax_credits?state=CA` |
| Pro | RevenueCat SDK; `GET /api/v1/books/entitlements` as a server-side mirror |

Run the server from the repository root with `python sovereign_dashboard_server.py`
(port 8090). The emulator reaches it at `http://10.0.2.2:8090`.

Store submission steps live in `docs/play-store/`.
