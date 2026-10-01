package com.sovereignengine.books.ui

import android.app.Activity
import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.revenuecat.purchases.Offerings
import com.revenuecat.purchases.Package
import com.sovereignengine.books.BuildConfig
import com.sovereignengine.books.billing.RevenueCatManager
import com.sovereignengine.books.data.AgentActivity
import com.sovereignengine.books.data.AppSettings
import com.sovereignengine.books.data.ApprovalCard
import com.sovereignengine.books.data.BooksApi
import com.sovereignengine.books.data.BooksRepository
import com.sovereignengine.books.data.HomeSnapshot
import com.sovereignengine.books.data.Runway
import com.sovereignengine.books.data.TaxCreditEstimate
import com.sovereignengine.books.data.TaxOpportunity
import com.sovereignengine.books.data.TaxSummary
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

data class UiState(
    val loading: Boolean = true,
    val offline: Boolean = false,
    val home: HomeSnapshot? = null,
    val runway: Runway? = null,
    val cards: List<ApprovalCard> = emptyList(),
    val decided: Int = 0,
    val credits: TaxCreditEstimate? = null,
    val creditsState: String = "CA",
    val taxSummary: TaxSummary? = null,
    val opportunities: List<TaxOpportunity> = emptyList(),
    val activity: List<AgentActivity> = emptyList(),
    val isPro: Boolean = false,
    val billingConfigured: Boolean = false,
    val offerings: Offerings? = null,
    val approvalsUsedToday: Int = 0,
    val showPaywall: Boolean = false,
    val message: String? = null,
    val apiBaseUrl: String = "",
    val appUserId: String = "",
    val demoMode: Boolean = false,
    val versionName: String = BuildConfig.VERSION_NAME,
) {
    val freeLimitReached: Boolean
        get() = !isPro && approvalsUsedToday >= AppSettings.FREE_DAILY_APPROVALS
}

class MainViewModel(app: Application) : AndroidViewModel(app) {

    private val settings = AppSettings(app)
    private val repo = BooksRepository(BooksApi { settings.apiBaseUrl }, settings)

    private val _state = MutableStateFlow(
        UiState(
            apiBaseUrl = settings.apiBaseUrl,
            appUserId = settings.appUserId,
            demoMode = settings.demoMode,
            billingConfigured = RevenueCatManager.isConfigured,
            approvalsUsedToday = settings.approvalsUsedToday(),
        ),
    )
    val state: StateFlow<UiState> = _state

    init {
        load()
        refreshEntitlement()
    }

    fun load() {
        _state.update { it.copy(loading = true, message = null) }
        viewModelScope.launch {
            val data = repo.load(_state.value.creditsState)
            _state.update {
                it.copy(
                    loading = false,
                    offline = data.offline,
                    home = data.home,
                    runway = data.runway,
                    cards = data.cards,
                    decided = 0,
                    credits = data.credits,
                    taxSummary = data.taxSummary,
                    opportunities = data.opportunities,
                    activity = data.activity,
                    message = if (data.offline && !settings.demoMode) "Could not reach the books API. Showing sample data." else null,
                )
            }
        }
    }

    fun refreshEntitlement() {
        viewModelScope.launch {
            val pro = RevenueCatManager.isPro() || (!settings.demoMode && repo.serverSaysPro())
            val offerings = _state.value.offerings ?: RevenueCatManager.offerings()
            _state.update { it.copy(isPro = pro, offerings = offerings, billingConfigured = RevenueCatManager.isConfigured) }
        }
    }

    /** Approve the top card. Returns false when the free limit blocks it. */
    fun approve(card: ApprovalCard, answer: String? = null): Boolean {
        val s = _state.value
        if (s.freeLimitReached) {
            _state.update { it.copy(showPaywall = true) }
            return false
        }
        viewModelScope.launch {
            repo.approve(card, answer)
            if (!s.isPro) settings.recordApproval()
            _state.update {
                it.copy(
                    cards = it.cards.filterNot { c -> c.id == card.id },
                    decided = it.decided + 1,
                    approvalsUsedToday = settings.approvalsUsedToday(),
                    activity = listOf(AgentActivity("Now", describeApproval(card, answer))) + it.activity,
                )
            }
            if (card is ApprovalCard.MealQuestion) refreshTax()
        }
        return true
    }

    private suspend fun refreshTax() {
        val opps = repo.opportunities(_state.value.creditsState)
        _state.update { it.copy(opportunities = opps) }
    }

    fun skip(card: ApprovalCard) {
        _state.update { it.copy(cards = it.cards.filterNot { c -> c.id == card.id }, decided = it.decided + 1) }
        viewModelScope.launch { repo.skip(card) }
    }

    fun setCreditsState(state: String) {
        _state.update { it.copy(creditsState = state) }
        viewModelScope.launch {
            val est = repo.taxCredits(state)
            val opps = repo.opportunities(state)
            _state.update { it.copy(credits = est, opportunities = opps) }
        }
    }

    fun showPaywall(show: Boolean) = _state.update { it.copy(showPaywall = show) }

    fun purchase(activity: Activity, pkg: Package) {
        viewModelScope.launch {
            when (val outcome = RevenueCatManager.purchase(activity, pkg)) {
                RevenueCatManager.PurchaseOutcome.Pro -> _state.update { it.copy(isPro = true, showPaywall = false, message = "Pro is active. Thank you.") }
                RevenueCatManager.PurchaseOutcome.Cancelled -> Unit
                is RevenueCatManager.PurchaseOutcome.Failed -> _state.update { it.copy(message = outcome.message) }
            }
        }
    }

    fun onPurchaseCompleted() = _state.update { it.copy(isPro = true, showPaywall = false, message = "Pro is active. Thank you.") }

    fun restore() {
        viewModelScope.launch {
            val pro = RevenueCatManager.restore()
            _state.update { it.copy(isPro = pro || it.isPro, message = if (pro) "Purchases restored." else "No active subscription found for this account.") }
        }
    }

    fun saveSettings(apiBaseUrl: String, appUserId: String, demoMode: Boolean) {
        settings.apiBaseUrl = apiBaseUrl
        if (appUserId.isNotBlank()) settings.setAppUserId(appUserId)
        settings.demoMode = demoMode
        _state.update { it.copy(apiBaseUrl = settings.apiBaseUrl, appUserId = settings.appUserId, demoMode = demoMode) }
        load()
    }

    fun clearMessage() = _state.update { it.copy(message = null) }

    private fun describeApproval(card: ApprovalCard, answer: String?): String = when (card) {
        is ApprovalCard.Categorize -> "Confirmed ${card.txn.merchant} as ${card.txn.categorySuggested ?: "uncategorized"}; rule learned"
        is ApprovalCard.MealQuestion -> {
            val pct = card.q.answers.firstOrNull { it.id == answer }?.deductiblePct ?: 0.5
            "${card.q.merchant}: ${(pct * 100).toInt()}% deductible"
        }
        is ApprovalCard.TaxCredit -> "Approved the ${card.estimate.jurisdiction.removePrefix("US_")} research credit claim file"
        is ApprovalCard.InvoiceChase -> "Sent follow-up to ${card.invoice.customer}"
    }
}
