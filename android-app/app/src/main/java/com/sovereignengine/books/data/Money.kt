package com.sovereignengine.books.data

import java.text.NumberFormat
import java.util.Locale

object Money {
    private val usd: NumberFormat = NumberFormat.getCurrencyInstance(Locale.US).apply {
        maximumFractionDigits = 0
    }
    private val usdCents: NumberFormat = NumberFormat.getCurrencyInstance(Locale.US)

    fun format(amount: Double): String = usd.format(amount)

    fun formatCents(amount: Double): String = usdCents.format(amount)
}
