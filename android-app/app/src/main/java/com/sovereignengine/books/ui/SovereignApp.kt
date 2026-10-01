package com.sovereignengine.books.ui

import android.app.Activity
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.AccountBalanceWallet
import androidx.compose.material.icons.outlined.Checklist
import androidx.compose.material.icons.outlined.Savings
import androidx.compose.material.icons.outlined.Settings
import androidx.compose.material.icons.outlined.WorkspacePremium
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.res.stringResource
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.sovereignengine.books.R
import com.sovereignengine.books.ui.screens.ApprovalsScreen
import com.sovereignengine.books.ui.screens.CreditsScreen
import com.sovereignengine.books.ui.screens.HomeScreen
import com.sovereignengine.books.ui.screens.PaywallHost
import com.sovereignengine.books.ui.screens.ProScreen
import com.sovereignengine.books.ui.screens.SettingsScreen

enum class Tab(val labelRes: Int, val icon: ImageVector) {
    Home(R.string.nav_home, Icons.Outlined.AccountBalanceWallet),
    Approvals(R.string.nav_approvals, Icons.Outlined.Checklist),
    Credits(R.string.nav_credits, Icons.Outlined.Savings),
    Pro(R.string.nav_pro, Icons.Outlined.WorkspacePremium),
    Settings(R.string.nav_settings, Icons.Outlined.Settings),
}

@Composable
fun SovereignApp(viewModel: MainViewModel, activity: Activity) {
    val state by viewModel.state.collectAsStateWithLifecycle()
    var tab by rememberSaveable { mutableStateOf(Tab.Home) }
    val snackbar = remember { SnackbarHostState() }

    LaunchedEffect(state.message) {
        val msg = state.message ?: return@LaunchedEffect
        snackbar.showSnackbar(msg)
        viewModel.clearMessage()
    }

    Scaffold(
        snackbarHost = { SnackbarHost(snackbar) },
        bottomBar = {
            NavigationBar {
                Tab.entries.forEach { t ->
                    NavigationBarItem(
                        selected = tab == t,
                        onClick = { tab = t },
                        icon = { Icon(t.icon, contentDescription = null) },
                        label = { Text(stringResource(t.labelRes)) },
                    )
                }
            }
        },
    ) { padding ->
        val modifier = Modifier.padding(padding)
        when (tab) {
            Tab.Home -> HomeScreen(state, modifier, onReview = { tab = Tab.Approvals }, onRetry = viewModel::load)
            Tab.Approvals -> ApprovalsScreen(
                state = state,
                modifier = modifier,
                onApprove = { card, answer -> viewModel.approve(card, answer) },
                onSkip = viewModel::skip,
                onUpgrade = { viewModel.showPaywall(true) },
            )
            Tab.Credits -> CreditsScreen(state, modifier, onState = viewModel::setCreditsState, onUpgrade = { viewModel.showPaywall(true) })
            Tab.Pro -> ProScreen(
                state = state,
                modifier = modifier,
                onSeePlans = { viewModel.showPaywall(true) },
                onRestore = viewModel::restore,
                onPurchase = { pkg -> viewModel.purchase(activity, pkg) },
            )
            Tab.Settings -> SettingsScreen(state, modifier, onSave = viewModel::saveSettings)
        }
    }

    PaywallHost(
        show = state.showPaywall,
        configured = state.billingConfigured,
        onDismiss = { viewModel.showPaywall(false) },
        onPurchased = viewModel::onPurchaseCompleted,
    )
}
