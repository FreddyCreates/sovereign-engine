package com.sovereign.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Initialize RevenueCat Android SDK
        RevenueCatManager.initialize(this)

        // Register IoT Hardware Device & Wear OS Node
        IoTRelayService.registerDevice("IOT_WEAR_OS_01", "WEAR_OS_WATCH", "US")
        IoTRelayService.registerDevice("IOT_NODE_EUROPE_02", "SMART_NODE", "DE")

        setContent {
            SovereignAppUI(activity = this)
        }
    }
}

@Composable
fun SovereignAppUI(activity: android.app.Activity) {
    var isProActive by remember { mutableStateOf(false) }
    var statusText by remember { mutableStateOf("Checking Subscription Status...") }

    LaunchedEffect(Unit) {
        RevenueCatManager.checkProEntitlement { active ->
            isProActive = active
            statusText = if (active) "★ PRO ACTIVE (Google Play / App Store)" else "Free Tier (Standard Access)"
        }
    }

    Surface(
        modifier = Modifier.fillMaxSize(),
        color = Color(0xFF06070A)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            // Header
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "AGENTIC QUICKBOOKS",
                    color = Color.White,
                    fontSize = 20.sp,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "RevenueCat Substrate",
                    color = Color(0xFF00E676),
                    fontSize = 12.sp,
                    fontWeight = FontWeight.SemiBold
                )
            }

            // Main Product Banner
            Card(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(20.dp),
                colors = CardDefaults.cardColors(containerColor = Color(0xFF12141D))
            ) {
                Column(
                    modifier = Modifier.padding(24.dp),
                    horizontalAlignment = Alignment.Start
                ) {
                    Text(
                        text = "Autonomous Bookkeeping Agent",
                        color = Color(0xFF94A3B8),
                        fontSize = 14.sp
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = "GAAP Accrual & Tax Credits",
                        color = Color.White,
                        fontSize = 22.sp,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.height(12.dp))
                    Text(
                        text = "• RevenueCat Subscription Monetization\n• Usage Metering & Overages\n• ASC 606 Ratable Revenue\n• Section 41 R&D Credits",
                        color = Color(0xFFCBD5E1),
                        fontSize = 13.sp,
                        lineHeight = 18.sp
                    )
                    Spacer(modifier = Modifier.height(16.dp))
                    Text(
                        text = statusText,
                        color = if (isProActive) Color(0xFF00E676) else Color(0xFFFF527B),
                        fontSize = 14.sp,
                        fontWeight = FontWeight.Bold
                    )
                }
            }

            // Actions
            Column(modifier = Modifier.fillMaxWidth()) {
                Button(
                    onClick = {
                        statusText = "Launching RevenueCat Paywall v2..."
                        // In live app: PaywallActivityLauncher.launch(activity)
                    },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(56.dp),
                    shape = RoundedCornerShape(12.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF7B52FF))
                ) {
                    Text(
                        text = "Upgrade via Google Play / App Store",
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Bold
                    )
                }
                
                Spacer(modifier = Modifier.height(12.dp))
                
                OutlinedButton(
                    onClick = {
                        statusText = "Restoring Store Purchases..."
                    },
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Text(text = "Restore Store Purchases", color = Color.White)
                }
            }
        }
    }
}
