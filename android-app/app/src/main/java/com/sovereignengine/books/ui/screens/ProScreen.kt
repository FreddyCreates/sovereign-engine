package com.sovereignengine.books.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import com.revenuecat.purchases.CustomerInfo
import com.revenuecat.purchases.Package
import com.revenuecat.purchases.models.StoreTransaction
import com.revenuecat.purchases.ui.revenuecatui.PaywallDialog
import com.revenuecat.purchases.ui.revenuecatui.PaywallDialogOptions
import com.revenuecat.purchases.ui.revenuecatui.PaywallListener
import com.revenuecat.purchases.ui.revenuecatui.customercenter.CustomerCenter
import com.sovereignengine.books.R
import com.sovereignengine.books.billing.RevenueCatManager
import com.sovereignengine.books.ui.UiState
import com.sovereignengine.books.ui.theme.Emerald
import com.sovereignengine.books.ui.theme.Slate

@Composable
fun ProScreen(
    state: UiState,
    modifier: Modifier = Modifier,
    onSeePlans: () -> Unit,
    onRestore: () -> Unit,
    onPurchase: (Package) -> Unit,
) {
    var showCustomerCenter by remember { mutableStateOf(false) }

    Column(modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(ScreenPadding), verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Text(stringResource(R.string.pro_title), style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
        SectionCard {
            Pill(if (state.isPro) stringResource(R.string.pro_active) else stringResource(R.string.pro_inactive), if (state.isPro) Emerald else Slate)
            Gap(12)
            Text(stringResource(R.string.pro_body), style = MaterialTheme.typography.bodyMedium)
            Gap(16)
            if (!state.billingConfigured) {
                Text(stringResource(R.string.pro_not_configured), color = Slate, style = MaterialTheme.typography.bodySmall)
            } else if (!state.isPro) {
                Button(onClick = onSeePlans, modifier = Modifier.fillMaxWidth()) { Text(stringResource(R.string.pro_upgrade)) }
            } else {
                OutlinedButton(onClick = { showCustomerCenter = true }, modifier = Modifier.fillMaxWidth()) { Text(stringResource(R.string.pro_manage)) }
            }
            TextButton(onClick = onRestore, modifier = Modifier.fillMaxWidth(), enabled = state.billingConfigured) { Text(stringResource(R.string.pro_restore)) }
        }

        // Plain package list as a fallback when the dashboard has no Paywall template.
        val packages = state.offerings?.current?.availablePackages.orEmpty()
        if (!state.isPro && packages.isNotEmpty()) {
            SectionCard {
                Label("Plans")
                Gap(6)
                packages.forEach { pkg ->
                    Row(Modifier.fillMaxWidth().padding(vertical = 6.dp), horizontalArrangement = Arrangement.SpaceBetween) {
                        Column(Modifier.weight(1f)) {
                            Text(pkg.product.title, style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.SemiBold)
                            Text(pkg.product.price.formatted, color = Slate, style = MaterialTheme.typography.bodySmall)
                        }
                        Button(onClick = { onPurchase(pkg) }) { Text("Choose") }
                    }
                }
            }
        }
    }

    if (showCustomerCenter) {
        Dialog(onDismissRequest = { showCustomerCenter = false }, properties = DialogProperties(usePlatformDefaultWidth = false)) {
            CustomerCenter(modifier = Modifier.fillMaxSize(), onDismiss = { showCustomerCenter = false })
        }
    }
}

/** RevenueCat Paywall (template configured in the dashboard), shown as a dialog. */
@Composable
fun PaywallHost(show: Boolean, configured: Boolean, onDismiss: () -> Unit, onPurchased: () -> Unit) {
    if (!show || !configured) return
    PaywallDialog(
        PaywallDialogOptions.Builder()
            .setDismissRequest(onDismiss)
            .setRequiredEntitlementIdentifier(RevenueCatManager.entitlementId)
            .setListener(object : PaywallListener {
                override fun onPurchaseCompleted(customerInfo: CustomerInfo, storeTransaction: StoreTransaction) {
                    if (RevenueCatManager.isPro(customerInfo)) onPurchased()
                }

                override fun onRestoreCompleted(customerInfo: CustomerInfo) {
                    if (RevenueCatManager.isPro(customerInfo)) onPurchased()
                }
            })
            .build(),
    )
}
