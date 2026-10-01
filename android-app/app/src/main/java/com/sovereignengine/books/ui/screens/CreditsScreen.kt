package com.sovereignengine.books.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.blur
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.sovereignengine.books.data.TaxOpportunity
import com.sovereignengine.books.ui.theme.Amber
import com.sovereignengine.books.ui.theme.Violet
import com.sovereignengine.books.R
import com.sovereignengine.books.data.Money
import com.sovereignengine.books.ui.UiState
import com.sovereignengine.books.ui.theme.Emerald
import com.sovereignengine.books.ui.theme.Slate

private val STATES = listOf("CA", "NY", "TX", "WA", "FL")

@Composable
fun CreditsScreen(state: UiState, modifier: Modifier = Modifier, onState: (String) -> Unit, onUpgrade: () -> Unit) {
    val est = state.credits
    val locked = !state.isPro
    Column(modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(ScreenPadding), verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Text(stringResource(R.string.credits_title), style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
        Row(Modifier.horizontalScroll(rememberScrollState()), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Text(stringResource(R.string.credits_state_picker), color = Slate, modifier = Modifier.padding(top = 10.dp))
            STATES.forEach { s ->
                FilterChip(selected = state.creditsState == s, onClick = { onState(s) }, label = { Text(s) })
            }
        }
        val next = state.opportunities.firstOrNull()
        if (next != null) {
            SectionCard {
                Label(stringResource(R.string.credits_next))
                Gap(6)
                OpportunityRow(next, highlight = true)
            }
        }
        state.taxSummary?.let { ts ->
            SectionCard {
                Label(stringResource(R.string.credits_deductions))
                Gap(6)
                StatRow(stringResource(R.string.credits_deductible), Money.format(ts.totalDeductible), bold = true)
                StatRow(stringResource(R.string.credits_nondeductible), Money.format(ts.totalNondeductible))
                StatRow(stringResource(R.string.credits_open), ts.openQuestions.toString())
            }
        }
        if (state.opportunities.size > 1) {
            SectionCard {
                Label(stringResource(R.string.credits_opportunities))
                Gap(6)
                val visible = if (locked) state.opportunities.drop(1).take(2) else state.opportunities.drop(1)
                visible.forEach { OpportunityRow(it) }
                if (locked && state.opportunities.size > 3) {
                    Gap(8)
                    Text(stringResource(R.string.credits_more_locked, state.opportunities.size - 3), color = Slate, style = MaterialTheme.typography.bodySmall)
                }
            }
        }
        if (locked) {
            SectionCard {
                Text(stringResource(R.string.credits_locked), style = MaterialTheme.typography.bodyMedium)
                Gap(12)
                Button(onClick = onUpgrade, modifier = Modifier.fillMaxWidth()) { Text(stringResource(R.string.pro_upgrade)) }
            }
        }
        val blur = if (locked) Modifier.blur(10.dp) else Modifier
        Text(stringResource(R.string.credits_research), style = MaterialTheme.typography.titleSmall, color = Slate)
        SectionCard(blur) {
            Label(stringResource(R.string.credits_total))
            Gap(6)
            BigNumber(Money.format(est?.totalCredits ?: 0.0), color = Emerald)
            Gap(12)
            StatRow("Federal Section 41", Money.format(est?.federalCredit ?: 0.0))
            StatRow(stringResource(R.string.credits_state), Money.format(est?.stateCredit ?: 0.0))
            StatRow("Section 174 amortization deduction", Money.format(est?.amortizationDeduction ?: 0.0))
        }
        SectionCard(blur) {
            Label(stringResource(R.string.credits_qre))
            Gap(6)
            StatRow("Engineering payroll", Money.format(est?.payrollQre ?: 0.0))
            StatRow("Cloud compute", Money.format(est?.cloudQre ?: 0.0))
            StatRow("Total", Money.format(est?.totalQre ?: 0.0), bold = true)
        }
        state.taxSummary?.byClass?.takeIf { it.isNotEmpty() && !locked }?.let { classes ->
            SectionCard {
                Label(stringResource(R.string.credits_by_class))
                Gap(6)
                classes.take(8).forEach { c ->
                    StatRow("${c.label} · ${(c.deductiblePct * 100).toInt()}%", Money.format(c.deductible))
                }
            }
        }
        val refs = est?.references.orEmpty()
        if (!locked && refs.isNotEmpty()) {
            SectionCard {
                Label(stringResource(R.string.credits_refs))
                Gap(6)
                refs.forEach { Text("• $it", style = MaterialTheme.typography.bodySmall, modifier = Modifier.padding(vertical = 2.dp)) }
            }
        }
        Text(
            "Estimates only. Credits are claimed on your return by a tax professional; the app assembles the evidence.",
            color = Slate,
            style = MaterialTheme.typography.bodySmall,
        )
    }
}

@Composable
private fun OpportunityRow(o: TaxOpportunity, highlight: Boolean = false) {
    val (statusText, statusColor) = when (o.status) {
        "qualified" -> stringResource(R.string.credits_status_qualified) to Emerald
        "not_yet" -> stringResource(R.string.credits_status_not_yet) to Slate
        else -> stringResource(R.string.credits_status_close) to Amber
    }
    Column(Modifier.padding(vertical = 6.dp)) {
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
            Text(o.title, style = if (highlight) MaterialTheme.typography.titleMedium else MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.SemiBold, modifier = Modifier.weight(1f))
            Text(Money.format(o.estimatedValue), color = if (highlight) Emerald else MaterialTheme.colorScheme.onSurface, fontWeight = FontWeight.Bold)
        }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.padding(top = 4.dp)) {
            Pill(statusText, statusColor)
            o.deadline?.let { Pill("by $it", Violet) }
        }
        Text(o.action, style = MaterialTheme.typography.bodySmall, modifier = Modifier.padding(top = 6.dp))
        Text(o.reference, style = MaterialTheme.typography.labelSmall, color = Slate, modifier = Modifier.padding(top = 2.dp))
    }
}

@Composable
private fun StatRow(label: String, value: String, bold: Boolean = false) {
    Row(Modifier.fillMaxWidth().padding(vertical = 4.dp), horizontalArrangement = Arrangement.SpaceBetween) {
        Text(label, color = Slate, style = MaterialTheme.typography.bodyMedium)
        Text(value, style = MaterialTheme.typography.bodyMedium, fontWeight = if (bold) FontWeight.Bold else FontWeight.Normal)
    }
}
