package com.sovereignengine.books.data

import android.content.Context
import android.content.SharedPreferences
import com.sovereignengine.books.BuildConfig
import java.time.LocalDate
import java.util.UUID

/** Per-device settings. Nothing here is sensitive; secrets never live in the app. */
class AppSettings(context: Context) {

    private val prefs: SharedPreferences =
        context.getSharedPreferences("sovereign_books", Context.MODE_PRIVATE)

    var apiBaseUrl: String
        get() = prefs.getString(KEY_API, null)?.takeIf { it.isNotBlank() } ?: BuildConfig.BOOKS_API_BASE_URL
        set(value) = prefs.edit().putString(KEY_API, value.trim().trimEnd('/')).apply()

    /** Stable anonymous id handed to RevenueCat and the books API. */
    val appUserId: String
        get() = prefs.getString(KEY_USER, null) ?: ("books_" + UUID.randomUUID().toString().replace("-", "").take(16)).also {
            prefs.edit().putString(KEY_USER, it).apply()
        }

    fun setAppUserId(value: String) = prefs.edit().putString(KEY_USER, value.trim()).apply()

    var demoMode: Boolean
        get() = prefs.getBoolean(KEY_DEMO, false)
        set(value) = prefs.edit().putBoolean(KEY_DEMO, value).apply()

    /** Approvals used today on the free plan. */
    fun approvalsUsedToday(): Int {
        val today = LocalDate.now().toString()
        if (prefs.getString(KEY_DAY, "") != today) return 0
        return prefs.getInt(KEY_COUNT, 0)
    }

    fun recordApproval() {
        val today = LocalDate.now().toString()
        val count = if (prefs.getString(KEY_DAY, "") == today) prefs.getInt(KEY_COUNT, 0) else 0
        prefs.edit().putString(KEY_DAY, today).putInt(KEY_COUNT, count + 1).apply()
    }

    companion object {
        private const val KEY_API = "api_base_url"
        private const val KEY_USER = "app_user_id"
        private const val KEY_DEMO = "demo_mode"
        private const val KEY_DAY = "approvals_day"
        private const val KEY_COUNT = "approvals_count"

        const val FREE_DAILY_APPROVALS = 5
    }
}
