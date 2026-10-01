package com.sovereignengine.books

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.viewModels
import com.sovereignengine.books.ui.MainViewModel
import com.sovereignengine.books.ui.SovereignApp
import com.sovereignengine.books.ui.theme.SovereignTheme

class MainActivity : ComponentActivity() {

    private val viewModel: MainViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        enableEdgeToEdge()
        super.onCreate(savedInstanceState)
        setContent {
            SovereignTheme {
                SovereignApp(viewModel = viewModel, activity = this)
            }
        }
    }

    override fun onResume() {
        super.onResume()
        viewModel.refreshEntitlement()
    }
}
