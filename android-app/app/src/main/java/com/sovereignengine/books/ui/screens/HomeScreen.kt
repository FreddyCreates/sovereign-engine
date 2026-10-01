package com.sovereignengine.books.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Button
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.sovereignengine.books.R
import com.sovereignengine.books.data.Money
import com.sovereignengine.books.ui.UiState
import com.sovereignengine.books.ui.theme.Amber
import com.sovereignengine.books.ui.theme.Emerald
import com.sovereignengine.books.ui.theme.Slate

@Composable
fun HomeScreen(state: UiState, modifier: Modifier = Modifier, onReview: () -> Unit, onRetry: () -> Unit) {
    LazyColumn(
        modifier = modifier.fillMaxSize(),
        contentPadding = ScreenPadding,
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        item {
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp), verticalAlignment = Alignment.CenterVertically) {
                Column(Modifier.weight(1f)) {
                    Text(state.home?.businessName ?: stringResource(R.string.app_name), style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
                    Text(stringResource(R.string.tagline), style = MaterialTheme.typography.bodySmall, color = Slate)
                }
                val (label, color) = when {
                    state.offline -> stringResource(R.string.home_bank_offline) to Amber
                    state.home?.bankConnected == true && state.home.mode == "live" -> stringResource(R.string.home_bank_connected) to Emerald
                    else -> stringResource(R.string.home_bank_demo) to Slate
                }
                Pill(label, color)
            }
        }
        if (state.loading) {
            item { LinearProgressIndicator(Modifier.fillMaxWidth()) }
        }
        item {
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                SectionCard(Modifier.weight(1f)) {
                    Label(stringResource(R.string.home_cash))
                    Gap(6)
                    BigNumber(Money.format(state.home?.cashBalance ?: 0.0))
                }
                SectionCard(Modifier.weight(1f)) {
                    Label(stringResource(R.string.home_runway))
                    Gap(6)
                    val months = state.runway?.monthsRunway
                    BigNumber(
                        if (months == null) "--" else stringResource(R.string.home_months, String.format("%.1f", months)),
                        color = if (months != null && months < 3) MaterialTheme.colorScheme.error else Emerald,
                    )
                }
            }
        }
        item {
            SectionCard {
                val n = state.cards.size
                Text(
                    if (n == 0) stringResource(R.string.home_all_clear) else stringResource(R.string.home_needs_you, n),
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.SemiBold,
                )
                if (n > 0) {
                    Gap(12)
                    Button(onClick = onReview, modifier = Modifier.fillMaxWidth()) { Text(stringResource(R.string.home_review)) }
                }
            }
        }
        item {
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                Text(stringResource(R.string.home_agent_log), style = MaterialTheme.typography.titleSmall, color = Slate)
                if (state.offline) TextButton(onClick = onRetry) { Text(stringResource(R.string.retry)) }
            }
        }
        items(state.activity) { entry ->
            Row(Modifier.fillMaxWidth().padding(vertical = 4.dp)) {
                Text(entry.time, style = MaterialTheme.typography.labelMedium, color = Slate, modifier = Modifier.width(56.dp))
                Text(entry.text, style = MaterialTheme.typography.bodyMedium)
            }
        }
    }
}
