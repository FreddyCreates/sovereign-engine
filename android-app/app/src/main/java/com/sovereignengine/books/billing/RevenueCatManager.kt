package com.sovereignengine.books.billing

import android.app.Activity
import android.content.Context
import android.util.Log
import com.revenuecat.purchases.CustomerInfo
import com.revenuecat.purchases.LogLevel
import com.revenuecat.purchases.Offerings
import com.revenuecat.purchases.Package
import com.revenuecat.purchases.PurchaseParams
import com.revenuecat.purchases.Purchases
import com.revenuecat.purchases.PurchasesConfiguration
import com.revenuecat.purchases.PurchasesTransactionException
import com.revenuecat.purchases.awaitCustomerInfo
import com.revenuecat.purchases.awaitOfferings
import com.revenuecat.purchases.awaitPurchase
import com.revenuecat.purchases.awaitRestore
import com.sovereignengine.books.BuildConfig

/**
 * Single entry point for RevenueCat. The public SDK key comes from BuildConfig,
 * which is populated from local.properties or the environment at build time.
 */
object RevenueCatManager {
    private const val TAG = "RevenueCat"

    val entitlementId: String = BuildConfig.REVENUECAT_ENTITLEMENT_ID

    /** False when the build has no SDK key, which makes every billing call a no-op. */
    val isConfigured: Boolean
        get() = BuildConfig.REVENUECAT_GOOGLE_API_KEY.isNotBlank() && Purchases.isConfigured

    fun configure(context: Context, appUserId: String) {
        val key = BuildConfig.REVENUECAT_GOOGLE_API_KEY
        if (key.isBlank()) {
            Log.w(TAG, "REVENUECAT_GOOGLE_API_KEY is empty; purchases disabled in this build")
            return
        }
        if (Purchases.isConfigured) return
        Purchases.logLevel = if (BuildConfig.DEBUG) LogLevel.DEBUG else LogLevel.WARN
        Purchases.configure(
            PurchasesConfiguration.Builder(context, key)
                .appUserID(appUserId)
                .build(),
        )
    }

    fun isPro(info: CustomerInfo): Boolean = info.entitlements[entitlementId]?.isActive == true

    suspend fun isPro(): Boolean {
        if (!isConfigured) return false
        return runCatching { isPro(Purchases.sharedInstance.awaitCustomerInfo()) }
            .onFailure { Log.w(TAG, "customer info failed", it) }
            .getOrDefault(false)
    }

    suspend fun offerings(): Offerings? {
        if (!isConfigured) return null
        return runCatching { Purchases.sharedInstance.awaitOfferings() }
            .onFailure { Log.w(TAG, "offerings failed", it) }
            .getOrNull()
    }

    sealed class PurchaseOutcome {
        data object Pro : PurchaseOutcome()
        data object Cancelled : PurchaseOutcome()
        data class Failed(val message: String) : PurchaseOutcome()
    }

    suspend fun purchase(activity: Activity, pkg: Package): PurchaseOutcome {
        if (!isConfigured) return PurchaseOutcome.Failed("Purchases are not configured in this build")
        return try {
            val result = Purchases.sharedInstance.awaitPurchase(PurchaseParams.Builder(activity, pkg).build())
            if (isPro(result.customerInfo)) PurchaseOutcome.Pro else PurchaseOutcome.Failed("Purchase completed but entitlement is not active")
        } catch (e: PurchasesTransactionException) {
            if (e.userCancelled) PurchaseOutcome.Cancelled else PurchaseOutcome.Failed(e.message)
        } catch (e: Exception) {
            PurchaseOutcome.Failed(e.message ?: "Purchase failed")
        }
    }

    suspend fun restore(): Boolean {
        if (!isConfigured) return false
        return runCatching { isPro(Purchases.sharedInstance.awaitRestore()) }
            .onFailure { Log.w(TAG, "restore failed", it) }
            .getOrDefault(false)
    }
}
