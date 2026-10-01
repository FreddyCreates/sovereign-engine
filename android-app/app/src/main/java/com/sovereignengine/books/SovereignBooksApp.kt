package com.sovereignengine.books

import android.app.Application
import com.sovereignengine.books.billing.RevenueCatManager
import com.sovereignengine.books.data.AppSettings

class SovereignBooksApp : Application() {
    override fun onCreate() {
        super.onCreate()
        val settings = AppSettings(this)
        RevenueCatManager.configure(this, settings.appUserId)
    }
}
