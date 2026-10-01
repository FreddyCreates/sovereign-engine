package com.sovereignengine.books.ui.screens

import android.content.Intent
import android.net.Uri
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
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.sovereignengine.books.R
import com.sovereignengine.books.ui.UiState
import com.sovereignengine.books.ui.theme.Slate

const val PRIVACY_POLICY_URL = "https://github.com/ThyFriendlyFox/sovereign-engine/blob/main/docs/play-store/privacy-policy.md"

@Composable
fun SettingsScreen(state: UiState, modifier: Modifier = Modifier, onSave: (String, String, Boolean) -> Unit) {
    val context = LocalContext.current
    var api by rememberSaveable(state.apiBaseUrl) { mutableStateOf(state.apiBaseUrl) }
    var user by rememberSaveable(state.appUserId) { mutableStateOf(state.appUserId) }
    var demo by rememberSaveable(state.demoMode) { mutableStateOf(state.demoMode) }

    Column(modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(ScreenPadding), verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Text(stringResource(R.string.nav_settings), style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
        SectionCard {
            Label(stringResource(R.string.settings_source))
            Gap(8)
            OutlinedTextField(
                value = api,
                onValueChange = { api = it },
                label = { Text(stringResource(R.string.settings_api)) },
                placeholder = { Text(stringResource(R.string.settings_api_hint)) },
                singleLine = true,
                modifier = Modifier.fillMaxWidth(),
            )
            Gap(8)
            OutlinedTextField(
                value = user,
                onValueChange = { user = it },
                label = { Text(stringResource(R.string.settings_user)) },
                singleLine = true,
                modifier = Modifier.fillMaxWidth(),
            )
            Gap(8)
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                Text(stringResource(R.string.settings_demo_mode), style = MaterialTheme.typography.bodyMedium)
                Switch(checked = demo, onCheckedChange = { demo = it })
            }
            Gap(12)
            Button(onClick = { onSave(api, user, demo) }, modifier = Modifier.fillMaxWidth()) { Text(stringResource(R.string.settings_save)) }
        }
        SectionCard {
            TextButton(onClick = {
                context.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(PRIVACY_POLICY_URL)))
            }) { Text(stringResource(R.string.settings_privacy)) }
            Text(stringResource(R.string.settings_version, state.versionName), color = Slate, style = MaterialTheme.typography.bodySmall, modifier = Modifier.padding(start = 12.dp))
        }
    }
}
