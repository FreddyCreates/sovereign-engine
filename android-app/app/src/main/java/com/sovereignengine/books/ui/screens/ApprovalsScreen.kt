package com.sovereignengine.books.ui.screens

import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.slideInHorizontally
import androidx.compose.animation.slideOutHorizontally
import androidx.compose.animation.togetherWith
import androidx.compose.foundation.gestures.detectHorizontalDragGestures
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.FilterChip
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.sovereignengine.books.R
import com.sovereignengine.books.data.AppSettings
import com.sovereignengine.books.data.ApprovalCard
import com.sovereignengine.books.data.Money
import com.sovereignengine.books.ui.UiState
import com.sovereignengine.books.ui.theme.Amber
import com.sovereignengine.books.ui.theme.Emerald
import com.sovereignengine.books.ui.theme.Slate
import com.sovereignengine.books.ui.theme.Violet

private const val SWIPE_THRESHOLD_PX = 220f

@Composable
fun ApprovalsScreen(
    state: UiState,
    modifier: Modifier = Modifier,
    onApprove: (ApprovalCard, String?) -> Boolean,
    onSkip: (ApprovalCard) -> Unit,
    onUpgrade: () -> Unit,
    initialAnswer: String? = null,
) {
    val card = state.cards.firstOrNull()
    var answer by remember(card?.id) { mutableStateOf(initialAnswer) }
    val canApprove = card != null && (card !is ApprovalCard.MealQuestion || answer != null)
    Column(modifier.fillMaxSize().padding(ScreenPadding)) {
        val total = state.cards.size + state.decided
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
            Text(stringResource(R.string.nav_approvals), style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
            if (total > 0) Text("${state.decided} / $total", color = Slate)
        }
        Gap(8)
        if (total > 0) LinearProgressIndicator(progress = { state.decided / total.toFloat() }, modifier = Modifier.fillMaxWidth())
        Gap(12)

        if (state.freeLimitReached && card != null) {
            SectionCard {
                Text(stringResource(R.string.approvals_locked, AppSettings.FREE_DAILY_APPROVALS), style = MaterialTheme.typography.bodyMedium)
                Gap(12)
                Button(onClick = onUpgrade, modifier = Modifier.fillMaxWidth()) { Text(stringResource(R.string.pro_upgrade)) }
            }
            Gap(12)
        }

        AnimatedContent(
            targetState = card,
            transitionSpec = {
                (slideInHorizontally { it / 3 } + fadeIn()) togetherWith (slideOutHorizontally { -it } + fadeOut())
            },
            label = "card",
            modifier = Modifier.weight(1f),
        ) { current ->
            if (current == null) {
                AllClear()
            } else {
                SwipeableCard(
                    key = current.id,
                    onApprove = { if (current is ApprovalCard.MealQuestion && answer == null) false else onApprove(current, answer) },
                    onSkip = { onSkip(current) },
                ) { CardBody(current, answer) { answer = it } }
            }
        }

        if (card != null) {
            Gap(12)
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                OutlinedButton(onClick = { onSkip(card) }, modifier = Modifier.weight(1f)) { Text(stringResource(R.string.skip)) }
                Button(
                    onClick = { onApprove(card, answer) },
                    enabled = canApprove,
                    modifier = Modifier.weight(1f),
                    colors = ButtonDefaults.buttonColors(containerColor = if (card is ApprovalCard.InvoiceChase) Violet else Emerald, contentColor = MaterialTheme.colorScheme.onSecondary),
                ) {
                    Text(if (card is ApprovalCard.InvoiceChase) stringResource(R.string.send) else stringResource(R.string.approve))
                }
            }
        }
    }
}

@Composable
private fun SwipeableCard(key: String, onApprove: () -> Boolean, onSkip: () -> Unit, content: @Composable () -> Unit) {
    var offset by remember(key) { mutableFloatStateOf(0f) }
    val animated by animateFloatAsState(offset, label = "offset")
    Box(
        Modifier
            .fillMaxSize()
            .graphicsLayer {
                translationX = animated
                rotationZ = animated / 60f
            }
            .pointerInput(key) {
                detectHorizontalDragGestures(
                    onDragEnd = {
                        when {
                            offset > SWIPE_THRESHOLD_PX -> { if (!onApprove()) offset = 0f }
                            offset < -SWIPE_THRESHOLD_PX -> onSkip()
                            else -> offset = 0f
                        }
                    },
                    onDragCancel = { offset = 0f },
                    onHorizontalDrag = { _, dragAmount -> offset += dragAmount },
                )
            },
    ) {
        SectionCard(Modifier.fillMaxSize()) {
            Column(Modifier.verticalScroll(rememberScrollState())) { content() }
        }
    }
}

@Composable
private fun AllClear() {
    Column(Modifier.fillMaxSize(), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Center) {
        Text(stringResource(R.string.approvals_done), style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold)
        Gap(8)
        Text(stringResource(R.string.approvals_done_body), color = Slate, style = MaterialTheme.typography.bodyMedium)
    }
}

@Composable
private fun CardBody(card: ApprovalCard, answer: String?, onAnswer: (String) -> Unit) {
    when (card) {
        is ApprovalCard.MealQuestion -> {
            Pill(stringResource(R.string.tax_question), Amber)
            Gap(12)
            Text(card.q.merchant, style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
            Text(card.q.date, color = Slate, style = MaterialTheme.typography.bodySmall)
            Gap(12)
            BigNumber(Money.formatCents(card.q.amount))
            Gap(16)
            Text(card.q.question, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
            Gap(4)
            Text(stringResource(R.string.tax_pick_answer), color = Slate, style = MaterialTheme.typography.bodySmall)
            Gap(8)
            FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                card.q.answers.forEach { a ->
                    FilterChip(
                        selected = answer == a.id,
                        onClick = { onAnswer(a.id) },
                        label = { Text("${a.label} · ${(a.deductiblePct * 100).toInt()}%") },
                    )
                }
            }
            val chosen = card.q.answers.firstOrNull { it.id == answer }
            if (chosen != null) {
                Gap(12)
                Text(
                    stringResource(R.string.tax_result, Money.formatCents(card.q.amount * chosen.deductiblePct), Money.formatCents(card.q.amount)),
                    color = if (chosen.deductiblePct > 0) Emerald else MaterialTheme.colorScheme.error,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                )
            }
        }
        is ApprovalCard.Categorize -> {
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Pill(stringResource(R.string.confirm_category), Violet)
                card.deductiblePct?.let { Pill(stringResource(R.string.tax_deductible_pct, (it * 100).toInt()), if (it > 0) Emerald else Slate) }
            }
            Gap(12)
            Text(card.txn.merchant, style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
            Text("${card.txn.date}  •  ${card.txn.accountName} ••${card.txn.mask}", color = Slate, style = MaterialTheme.typography.bodySmall)
            Gap(12)
            BigNumber(Money.formatCents(kotlin.math.abs(card.txn.amount)), color = if (card.txn.amount < 0) Emerald else MaterialTheme.colorScheme.onSurface)
            Gap(16)
            Label(stringResource(R.string.agent_confidence))
            Text("${card.confidence}%  →  ${card.txn.categorySuggested ?: "Needs a category"}", style = MaterialTheme.typography.titleMedium)
            card.taxLabel?.let { Text(it, color = Slate, style = MaterialTheme.typography.bodySmall) }
            if (card.similar.isNotEmpty()) {
                Gap(16)
                Label(stringResource(R.string.similar_charges))
                Gap(4)
                card.similar.forEach { s ->
                    Row(Modifier.fillMaxWidth().padding(vertical = 4.dp), horizontalArrangement = Arrangement.SpaceBetween) {
                        Text(s.date, color = Slate, style = MaterialTheme.typography.bodySmall)
                        Text(Money.formatCents(kotlin.math.abs(s.amount)), style = MaterialTheme.typography.bodySmall)
                    }
                    HorizontalDivider()
                }
            }
        }
        is ApprovalCard.TaxCredit -> {
            Pill(stringResource(R.string.credits_title), Emerald)
            Gap(12)
            Text("${card.estimate.jurisdiction.removePrefix("US_")} research credit", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
            Gap(12)
            BigNumber(Money.format(card.estimate.totalCredits), color = Emerald)
            Text("on ${Money.format(card.estimate.totalQre)} of qualified research expenses", color = Slate, style = MaterialTheme.typography.bodySmall)
            Gap(16)
            Label(stringResource(R.string.evidence))
            Gap(4)
            card.evidence.forEach { Text("• $it", style = MaterialTheme.typography.bodyMedium, modifier = Modifier.padding(vertical = 2.dp)) }
            Gap(12)
            Text("Approving builds the claim file in the background. Nothing is filed without your accountant.", color = Slate, style = MaterialTheme.typography.bodySmall)
        }
        is ApprovalCard.InvoiceChase -> {
            Pill("Invoice ${card.invoice.daysOverdue} days late", Amber)
            Gap(12)
            Text(card.invoice.customer, style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
            Gap(12)
            BigNumber(Money.formatCents(card.invoice.amount))
            Gap(16)
            Label("Draft follow-up")
            Gap(4)
            Text(card.draftEmail, style = MaterialTheme.typography.bodyMedium)
            Spacer(Modifier.height(8.dp))
        }
    }
}
