package com.sovereignengine.books.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

val Ink = Color(0xFF06070A)
val Surface1 = Color(0xFF12141D)
val Surface2 = Color(0xFF1A1D2A)
val Emerald = Color(0xFF00E676)
val Violet = Color(0xFF7B52FF)
val Rose = Color(0xFFFF527B)
val Slate = Color(0xFF94A3B8)
val Amber = Color(0xFFFFB547)

private val DarkScheme = darkColorScheme(
    primary = Violet,
    onPrimary = Color.White,
    secondary = Emerald,
    onSecondary = Ink,
    tertiary = Amber,
    background = Ink,
    onBackground = Color(0xFFF1F5F9),
    surface = Surface1,
    onSurface = Color(0xFFF1F5F9),
    surfaceVariant = Surface2,
    onSurfaceVariant = Slate,
    error = Rose,
    outline = Color(0xFF2A2F42),
)

private val LightScheme = lightColorScheme(
    primary = Violet,
    secondary = Color(0xFF00A854),
    tertiary = Color(0xFFB36B00),
    error = Color(0xFFD1365B),
)

@Composable
fun SovereignTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit,
) {
    MaterialTheme(
        colorScheme = if (darkTheme) DarkScheme else LightScheme,
        content = content,
    )
}
