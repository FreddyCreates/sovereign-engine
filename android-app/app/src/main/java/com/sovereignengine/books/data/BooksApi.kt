package com.sovereignengine.books.data

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.json.JSONObject
import java.io.IOException
import java.net.HttpURLConnection
import java.net.URL
import java.time.LocalDate
import java.time.temporal.ChronoUnit

/** Thin JSON client for sovereign_dashboard_server.py. All calls run on IO. */
class BooksApi(private val baseUrlProvider: () -> String) {

    suspend fun home(): HomeSnapshot = get("/api/v1/books/home").let { o ->
        HomeSnapshot(
            businessName = o.optString("business_name", "Your company"),
            cashBalance = o.optDouble("cash_balance", 0.0),
            inboxCount = o.optInt("inbox_count", 0),
            bankConnected = o.optBoolean("bank_connected", false),
            mode = o.optString("mode", "mock"),
        )
    }

    suspend fun inbox(limit: Int = 25): List<InboxTransaction> =
        get("/api/v1/books/inbox?limit=$limit").optJSONArray("transactions").toTransactions()

    suspend fun confirmTransaction(txnId: String, category: String?): JSONObject =
        post("/api/v1/books/transactions/confirm", JSONObject().apply {
            put("txn_id", txnId)
            if (category != null) put("category", category)
        })

    suspend fun runway(): Runway = get("/api/v1/books/runway").let { o ->
        Runway(
            monthsRunway = o.optDouble("months_runway", 0.0),
            cash = o.optDouble("cash", 0.0),
            message = o.optString("message", ""),
        )
    }

    suspend fun taxCredits(state: String): TaxCreditEstimate =
        get("/api/v1/agentic_qb/tax_credits?state=$state").toTaxCredit()

    suspend fun invoices(): List<Invoice> =
        get("/api/v1/books/invoices").optJSONArray("invoices").let { arr ->
            if (arr == null) return emptyList()
            (0 until arr.length()).map { arr.getJSONObject(it).toInvoice() }
        }

    /** Records a decision in the server-side approvals log. */
    suspend fun recordApproval(
        kind: String,
        decision: String,
        cardId: String,
        subject: String?,
        amount: Double?,
        payload: Map<String, Any?> = emptyMap(),
    ): JSONObject = post("/api/v1/books/approvals", JSONObject().apply {
        put("kind", kind)
        put("decision", decision)
        put("card_id", cardId)
        put("source", "mobile")
        if (subject != null) put("subject", subject)
        if (amount != null) put("amount", amount)
        put("payload", JSONObject(payload))
    })

    // --- tax ---------------------------------------------------------------

    suspend fun taxQuestions(limit: Int = 10): List<TaxQuestion> =
        get("/api/v1/books/tax/questions?limit=$limit").optJSONArray("questions").let { arr ->
            if (arr == null) return emptyList()
            (0 until arr.length()).map { i ->
                val o = arr.getJSONObject(i)
                val answers = o.optJSONArray("answers")?.let { a ->
                    (0 until a.length()).map { j ->
                        val x = a.getJSONObject(j)
                        TaxAnswer(x.optString("id"), x.optString("label"), x.optDouble("deductible_pct", 0.0))
                    }
                } ?: emptyList()
                TaxQuestion(
                    transactionId = o.optString("transaction_id"),
                    question = o.optString("question", "Who was this meal with?"),
                    answers = answers,
                    merchant = o.optString("merchant"),
                    date = o.optString("date"),
                    amount = o.optDouble("amount", 0.0),
                    currentDeductiblePct = o.optDouble("current_deductible_pct", 0.5),
                )
            }
        }

    suspend fun taxClassify(txnId: String, attendees: String): JSONObject =
        post("/api/v1/books/tax/classify", JSONObject().apply {
            put("txn_id", txnId)
            put("attendees", attendees)
        })

    /** Map of transaction id to (label, deductible pct) for chips on categorize cards. */
    suspend fun taxClassifications(): Map<String, Pair<String, Double>> =
        get("/api/v1/books/tax/classifications?limit=200").optJSONArray("classifications").let { arr ->
            if (arr == null) return emptyMap()
            (0 until arr.length()).associate { i ->
                val o = arr.getJSONObject(i)
                o.optString("transaction_id") to (o.optString("label") to o.optDouble("deductible_pct", 0.0))
            }
        }

    suspend fun taxSummary(): TaxSummary = get("/api/v1/books/tax/summary").let { o ->
        val arr = o.optJSONArray("by_class")
        TaxSummary(
            taxYear = o.optInt("tax_year"),
            totalSpent = o.optDouble("total_spent", 0.0),
            totalDeductible = o.optDouble("total_deductible", 0.0),
            totalNondeductible = o.optDouble("total_nondeductible", 0.0),
            openQuestions = o.optInt("open_questions", 0),
            byClass = arr?.let { a ->
                (0 until a.length()).map { i ->
                    val c = a.getJSONObject(i)
                    TaxClassTotal(c.optString("tax_class"), c.optString("label"), c.optDouble("deductible_pct", 0.0), c.optInt("count"), c.optDouble("spent", 0.0), c.optDouble("deductible", 0.0))
                }
            } ?: emptyList(),
        )
    }

    suspend fun taxOpportunities(state: String): List<TaxOpportunity> =
        get("/api/v1/books/tax/opportunities?state=$state").optJSONArray("opportunities").let { arr ->
            if (arr == null) return emptyList()
            (0 until arr.length()).map { i ->
                val o = arr.getJSONObject(i)
                TaxOpportunity(
                    id = o.optString("id"),
                    title = o.optString("title"),
                    action = o.optString("action"),
                    reference = o.optString("reference"),
                    status = o.optString("status", "close"),
                    estimatedValue = o.optDouble("estimated_value", 0.0),
                    valueNote = o.optString("value_note"),
                    gap = o.optString("gap"),
                    deadline = o.optString("deadline").takeIf { it.isNotBlank() && it != "null" },
                )
            }
        }

    suspend fun entitlements(appUserId: String): Boolean =
        get("/api/v1/books/entitlements?app_user_id=$appUserId").optBoolean("pro_active", false)

    // --- transport -------------------------------------------------------

    private suspend fun get(path: String): JSONObject = request("GET", path, null)

    private suspend fun post(path: String, body: JSONObject): JSONObject = request("POST", path, body)

    private suspend fun request(method: String, path: String, body: JSONObject?): JSONObject =
        withContext(Dispatchers.IO) {
            val url = URL(baseUrlProvider().trimEnd('/') + path)
            val conn = url.openConnection() as HttpURLConnection
            try {
                conn.requestMethod = method
                conn.connectTimeout = 6_000
                conn.readTimeout = 10_000
                conn.setRequestProperty("Accept", "application/json")
                if (body != null) {
                    conn.doOutput = true
                    conn.setRequestProperty("Content-Type", "application/json")
                    conn.outputStream.use { it.write(body.toString().toByteArray()) }
                }
                val code = conn.responseCode
                val stream = if (code in 200..299) conn.inputStream else conn.errorStream
                val text = stream?.bufferedReader()?.use { it.readText() } ?: ""
                if (code !in 200..299) throw IOException("HTTP $code from $path: ${text.take(200)}")
                JSONObject(text)
            } finally {
                conn.disconnect()
            }
        }

    // --- mapping ---------------------------------------------------------

    private fun JSONArray?.toTransactions(): List<InboxTransaction> {
        if (this == null) return emptyList()
        return (0 until length()).map { i ->
            val o = getJSONObject(i)
            InboxTransaction(
                id = o.optString("id"),
                date = o.optString("date"),
                name = o.optString("name"),
                merchant = o.optString("merchant_name", o.optString("name")),
                amount = o.optDouble("amount", 0.0),
                pending = o.optInt("pending", 0) == 1,
                categorySuggested = o.optString("category_suggested").takeIf { it.isNotBlank() && it != "null" },
                accountName = o.optString("account_name", ""),
                mask = o.optString("mask", ""),
            )
        }
    }

    private fun JSONObject.toTaxCredit(): TaxCreditEstimate {
        val refs = optJSONArray("statutory_references")?.let { arr ->
            (0 until arr.length()).map { i ->
                val r = arr.opt(i)
                if (r is JSONObject) r.optString("citation", r.optString("name", r.toString())) else r.toString()
            }
        } ?: emptyList()
        return TaxCreditEstimate(
            jurisdiction = optString("jurisdiction", "US"),
            cloudQre = optDouble("cloud_compute_qre", 0.0),
            payrollQre = optDouble("rd_payroll_qre", 0.0),
            totalQre = optDouble("total_qualified_research_expenses", 0.0),
            federalCredit = optDouble("federal_section_41_credit", 0.0),
            stateCredit = optDouble("state_tax_credit", 0.0),
            totalCredits = optDouble("total_estimated_tax_credits", 0.0),
            amortizationDeduction = optDouble("sec_174_annual_amortization_deduction", 0.0),
            references = refs,
        )
    }

    private fun JSONObject.toInvoice(): Invoice {
        val due = optString("due_date").takeIf { it.isNotBlank() && it != "null" }
        val overdue = due?.let {
            runCatching { ChronoUnit.DAYS.between(LocalDate.parse(it.take(10)), LocalDate.now()).toInt() }.getOrNull()
        } ?: 0
        return Invoice(
            id = optString("id"),
            customer = optString("customer", "Customer"),
            amount = optDouble("amount", 0.0),
            status = optString("status", "open"),
            dueDate = due,
            daysOverdue = overdue.coerceAtLeast(0),
        )
    }
}
