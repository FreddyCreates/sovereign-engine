package com.sovereign.app

import android.content.Context
import android.util.Log
import com.revenuecat.purchases.CustomerInfo
import com.revenuecat.purchases.Offerings
import com.revenuecat.purchases.Package
import com.revenuecat.purchases.Purchases
import com.revenuecat.purchases.PurchasesConfiguration
import com.revenuecat.purchases.PurchasesError
import com.revenuecat.purchases.interfaces.ReceiveCustomerInfoCallback
import com.revenuecat.purchases.interfaces.ReceiveOfferingsCallback
import com.revenuecat.purchases.interfaces.PurchaseCallback
import com.revenuecat.purchases.models.StoreTransaction

object RevenueCatManager {
    private const val TAG = "RevenueCatManager"
    private const val REVENUECAT_API_KEY = "goog_pub_live_sovereign_android_2026"

    fun initialize(context: Context, appUserId: String = "user_android_sovereign") {
        Log.i(TAG, "Initializing RevenueCat Android SDK for Google Play & Galaxy Store...")
        
        val configuration = PurchasesConfiguration.Builder(context, REVENUECAT_API_KEY)
            .appUserID(appUserId)
            .build()

        Purchases.configure(configuration)
        Log.i(TAG, "RevenueCat Android SDK configured successfully.")
    }

    fun fetchOfferings(onSuccess: (Offerings) -> Unit, onError: (PurchasesError) -> Unit) {
        Purchases.sharedInstance.getOfferings(object : ReceiveOfferingsCallback {
            override fun onReceived(offerings: Offerings) {
                Log.i(TAG, "Fetched Offerings: ${offerings.current?.identifier}")
                onSuccess(offerings)
            }

            override fun onError(error: PurchasesError) {
                Log.e(TAG, "Error fetching offerings: ${error.message}")
                onError(error)
            }
        })
    }

    fun purchasePackage(
        activity: android.app.Activity,
        pkg: Package,
        onSuccess: (StoreTransaction, CustomerInfo) -> Unit,
        onError: (PurchasesError, Boolean) -> Unit
    ) {
        Purchases.sharedInstance.purchase(
            activity = activity,
            packageToPurchase = pkg,
            callback = object : PurchaseCallback {
                override fun onCompleted(storeTransaction: StoreTransaction, customerInfo: CustomerInfo) {
                    Log.i(TAG, "Purchase completed successfully! Entitlements: ${customerInfo.entitlements.active.keys}")
                    onSuccess(storeTransaction, customerInfo)
                }

                override fun onError(error: PurchasesError, userCancelled: Boolean) {
                    Log.e(TAG, "Purchase error: ${error.message}")
                    onError(error, userCancelled)
                }
            }
        )
    }

    fun checkProEntitlement(onResult: (Boolean) -> Unit) {
        Purchases.sharedInstance.getCustomerInfo(object : ReceiveCustomerInfoCallback {
            override fun onReceived(customerInfo: CustomerInfo) {
                val isPro = customerInfo.entitlements["pro_access"]?.isActive == true
                onResult(isPro)
            }

            override fun onError(error: PurchasesError) {
                onResult(false)
            }
        })
    }
}
