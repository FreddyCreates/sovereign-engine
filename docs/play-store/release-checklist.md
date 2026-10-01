# Release checklist for Google Play

Work through this top to bottom. Anything marked **once** only has to happen the first time.

## 1. Accounts (once)

- [ ] Google Play Console developer account (one-time registration fee, identity verification can take days).
- [ ] RevenueCat project with a Google Play app. Copy the **public SDK key** (`goog_...`).
- [ ] In Play Console, create the app, package name `com.sovereignengine.books`.
- [ ] Link RevenueCat to Play: upload the Play service account JSON under RevenueCat > Project > Apps > Google Play.

## 2. Products (once)

- [ ] In Play Console > Monetize > Subscriptions, create `sovereign_pro_monthly` and `sovereign_pro_annual` with base plans and a free trial offer.
- [ ] In RevenueCat, import the products, create entitlement `pro_access`, and an offering `default` containing both packages.
- [ ] Optional: design a Paywall in RevenueCat > Paywalls. The app shows it through `PaywallDialog`; without one the Pro screen lists packages directly.
- [ ] Configure Customer Center in RevenueCat so "Manage subscription" works.

## 3. Build configuration

- [ ] Copy `android-app/local.properties.example` to `android-app/local.properties`.
- [ ] Set `REVENUECAT_GOOGLE_API_KEY`, `REVENUECAT_ENTITLEMENT_ID`, and the production `BOOKS_API_BASE_URL` (must be HTTPS).
- [ ] Create an upload keystore (once) and set `KEYSTORE_PATH`, `KEYSTORE_PASSWORD`, `KEY_ALIAS`, `KEY_PASSWORD`:
  ```bash
  keytool -genkeypair -v -keystore upload-keystore.jks -alias upload -keyalg RSA -keysize 2048 -validity 10000
  ```
- [ ] Bump `VERSION_CODE` (must increase on every upload) and `VERSION_NAME`.

## 4. Build

Locally:

```bash
cd android-app
./gradlew :app:bundleRelease
# -> app/build/outputs/bundle/release/app-release.aab
```

Or from GitHub Actions (`.github/workflows/android-release.yml`). Add these
repository secrets once: `ANDROID_KEYSTORE_BASE64` (`base64 -w0 upload-keystore.jks`),
`ANDROID_KEYSTORE_PASSWORD`, `ANDROID_KEY_ALIAS`, `ANDROID_KEY_PASSWORD`,
`REVENUECAT_GOOGLE_API_KEY`, and optionally `PLAY_SERVICE_ACCOUNT_JSON`; plus the
repository variable `BOOKS_API_BASE_URL`. Then either push a tag
(`git tag android-v1.0.0 && git push origin android-v1.0.0`) or run the
workflow by hand and pick the Play track. The signed bundle is attached to the
GitHub release and, when the service account secret is set, uploaded to Play.

Store screenshots are real renders of the app produced on the JVM:

```bash
cd android-app && ./gradlew :app:recordRoborazziDebug
# -> docs/play-store/screenshots/*.png (1080 x 1920)
```

For a quick device check:

```bash
./gradlew :app:assembleDebug
adb install app/build/outputs/apk/debug/app-debug.apk
```

## 5. Play Console

- [ ] App content: privacy policy URL, ads declaration (no ads), data safety (see `data-safety.md`), content rating questionnaire, target audience (18+ business tool), government app (no), financial features (declare "budgeting and expense tracking"; no loans or payments issued by the app).
- [ ] Store listing: copy from `store-listing.md`, 512 px icon, feature graphic, screenshots.
- [ ] Upload the AAB to **Internal testing** first. Install from the testing link and run through a purchase with a license tester account.
- [ ] New developer accounts must run a closed test with at least 12 testers for 14 days before production access is granted. Start this early.
- [ ] Promote to production and submit for review.

## 6. After release

- [ ] Verify a real purchase shows up in RevenueCat and that `pro_access` unlocks the Credits tab.
- [ ] Set the RevenueCat webhook to `https://<your api>/api/v1/books/revenuecat/webhook` with `REVENUECAT_WEBHOOK_AUTH` as the Authorization value so the server mirrors entitlements.
- [ ] Tag the commit: `git tag android-v1.0.0`.
