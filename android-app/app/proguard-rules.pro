# RevenueCat
-keep class com.revenuecat.purchases.** { *; }
-dontwarn com.revenuecat.purchases.**

# Keep BuildConfig so runtime settings stay readable.
-keep class com.sovereignengine.books.BuildConfig { *; }

# Kotlin coroutines
-dontwarn kotlinx.coroutines.**
