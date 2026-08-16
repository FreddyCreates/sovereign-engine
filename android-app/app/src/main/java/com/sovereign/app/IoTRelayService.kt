package com.sovereign.app

import android.util.Log
import com.revenuecat.purchases.CustomerInfo

object IoTRelayService {
    private const val TAG = "IoTRelayService"

    data class IoTDeviceState(
        val deviceId: String,
        val deviceType: String, // e.g. "WEAR_OS_WATCH", "SMART_NODE", "CONNECTED_CAR", "BIOMETRIC_SENSOR"
        val locationCountry: String,
        val isHardwareUnlocked: Boolean,
        val lastTelemetryPingMs: Long
    )

    private val connectedDevices = mutableMapOf<String, IoTDeviceState>()

    fun registerDevice(deviceId: String, deviceType: String, country: String) {
        val state = IoTDeviceState(
            deviceId = deviceId,
            deviceType = deviceType,
            locationCountry = country,
            isHardwareUnlocked = false,
            lastTelemetryPingMs = System.currentTimeMillis()
        )
        connectedDevices[deviceId] = state
        Log.i(TAG, "Registered IoT Hardware Device: $deviceId ($deviceType) in $country")
    }

    fun syncEntitlementsWithIoT(customerInfo: CustomerInfo) {
        val isProActive = customerInfo.entitlements["pro_access"]?.isActive == true
        val isEnterpriseActive = customerInfo.entitlements["enterprise_access"]?.isActive == true

        connectedDevices.keys.forEach { deviceId ->
            val existing = connectedDevices[deviceId]
            if (existing != null) {
                val shouldUnlock = isProActive || isEnterpriseActive
                connectedDevices[deviceId] = existing.copy(
                    isHardwareUnlocked = shouldUnlock,
                    lastTelemetryPingMs = System.currentTimeMillis()
                )
                Log.i(TAG, "IoT Hardware $deviceId ($existing.deviceType) -> Hardware Unlocked: $shouldUnlock (RevenueCat Subscription Sync)")
            }
        }
    }

    fun getConnectedDevices(): List<IoTDeviceState> = connectedDevices.values.toList()
}
