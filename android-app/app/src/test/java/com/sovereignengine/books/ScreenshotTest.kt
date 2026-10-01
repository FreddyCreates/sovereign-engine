package com.sovereignengine.books

import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onRoot
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.github.takahirom.roborazzi.RoborazziRule
import com.github.takahirom.roborazzi.captureRoboImage
import com.sovereignengine.books.data.ApprovalCard
import com.sovereignengine.books.data.DemoData
import com.sovereignengine.books.ui.UiState
import com.sovereignengine.books.ui.screens.ApprovalsScreen
import com.sovereignengine.books.ui.screens.CreditsScreen
import com.sovereignengine.books.ui.screens.HomeScreen
import com.sovereignengine.books.ui.screens.ProScreen
import com.sovereignengine.books.ui.screens.SettingsScreen
import com.sovereignengine.books.ui.theme.SovereignTheme
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.annotation.Config
import org.robolectric.annotation.GraphicsMode

/**
 * Renders every screen with the sample data on the JVM and writes PNGs for
 * the Play Store listing and the walkthrough. Run with:
 *   ./gradlew :app:recordRoborazziDebug
 */
@RunWith(AndroidJUnit4::class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
@Config(sdk = [34], qualifiers = "w360dp-h640dp-xxhdpi")
class ScreenshotTest {

    @get:Rule
    val composeRule = createComposeRule()

    @get:Rule
    val roborazziRule = RoborazziRule(
        composeRule = composeRule,
        captureRoot = composeRule.onRoot(),
        options = RoborazziRule.Options(outputDirectoryPath = "../../docs/play-store/screenshots"),
    )

    private val demo = DemoData.data

    private fun state(isPro: Boolean = false, cards: List<ApprovalCard> = demo.cards) = UiState(
        loading = false,
        offline = false,
        home = demo.home.copy(bankConnected = true, mode = "live"),
        runway = demo.runway,
        cards = cards,
        credits = demo.credits,
        taxSummary = demo.taxSummary,
        opportunities = demo.opportunities,
        activity = demo.activity,
        isPro = isPro,
        billingConfigured = true,
        apiBaseUrl = "https://api.sovereignbooks.app",
        appUserId = "books_demo",
        versionName = "1.0.0",
    )

    private fun shoot(name: String, content: @androidx.compose.runtime.Composable () -> Unit) {
        composeRule.setContent {
            SovereignTheme(darkTheme = true) {
                androidx.compose.material3.Surface(
                    modifier = androidx.compose.ui.Modifier.fillMaxSize(),
                    color = androidx.compose.material3.MaterialTheme.colorScheme.background,
                ) { content() }
            }
        }
        composeRule.onRoot().captureRoboImage("../../docs/play-store/screenshots/$name.png")
    }

    @Test
    fun home() = shoot("01-home") { HomeScreen(state(), onReview = {}, onRetry = {}) }

    @Test
    fun approvalsCategorize() = shoot("02-approvals-categorize") {
        ApprovalsScreen(state(), onApprove = { _, _ -> true }, onSkip = {}, onUpgrade = {})
    }

    @Test
    fun approvalsMealQuestion() = shoot("03-approvals-meal") {
        ApprovalsScreen(state(cards = demo.cards.filterIsInstance<ApprovalCard.MealQuestion>()), onApprove = { _, _ -> true }, onSkip = {}, onUpgrade = {}, initialAnswer = "all_employees")
    }

    @Test
    fun approvalsTaxCredit() = shoot("04-approvals-credit") {
        ApprovalsScreen(state(cards = demo.cards.filterIsInstance<ApprovalCard.TaxCredit>()), onApprove = { _, _ -> true }, onSkip = {}, onUpgrade = {})
    }

    @Test
    fun approvalsInvoice() = shoot("05-approvals-invoice") {
        ApprovalsScreen(state(cards = demo.cards.filterIsInstance<ApprovalCard.InvoiceChase>()), onApprove = { _, _ -> true }, onSkip = {}, onUpgrade = {})
    }

    @Test
    fun creditsPro() = shoot("06-credits") { CreditsScreen(state(isPro = true), onState = {}, onUpgrade = {}) }

    @Test
    fun creditsLocked() = shoot("07-credits-locked") { CreditsScreen(state(isPro = false), onState = {}, onUpgrade = {}) }

    @Test
    fun pro() = shoot("08-pro") { ProScreen(state(isPro = false), onSeePlans = {}, onRestore = {}, onPurchase = {}) }

    @Test
    fun settings() = shoot("09-settings") { SettingsScreen(state(), onSave = { _, _, _ -> }) }
}
