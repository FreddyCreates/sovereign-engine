package com.sovereignengine.books.data

data class HomeSnapshot(
    val businessName: String,
    val cashBalance: Double,
    val inboxCount: Int,
    val bankConnected: Boolean,
    val mode: String,
)

data class InboxTransaction(
    val id: String,
    val date: String,
    val name: String,
    val merchant: String,
    /** Plaid convention: positive is money out, negative is money in. */
    val amount: Double,
    val pending: Boolean,
    val categorySuggested: String?,
    val accountName: String,
    val mask: String,
)

data class Runway(
    val monthsRunway: Double,
    val cash: Double,
    val message: String,
)

data class TaxCreditEstimate(
    val jurisdiction: String,
    val cloudQre: Double,
    val payrollQre: Double,
    val totalQre: Double,
    val federalCredit: Double,
    val stateCredit: Double,
    val totalCredits: Double,
    val amortizationDeduction: Double,
    val references: List<String>,
)

data class Invoice(
    val id: String,
    val customer: String,
    val amount: Double,
    val status: String,
    val dueDate: String?,
    val daysOverdue: Int,
)

data class AgentActivity(
    val time: String,
    val text: String,
)

/** One decision the agents could not make alone. */
data class TaxAnswer(val id: String, val label: String, val deductiblePct: Double)

data class TaxQuestion(
    val transactionId: String,
    val question: String,
    val answers: List<TaxAnswer>,
    val merchant: String,
    val date: String,
    val amount: Double,
    val currentDeductiblePct: Double,
)

data class TaxClassTotal(
    val code: String,
    val label: String,
    val deductiblePct: Double,
    val count: Int,
    val spent: Double,
    val deductible: Double,
)

data class TaxSummary(
    val taxYear: Int,
    val totalSpent: Double,
    val totalDeductible: Double,
    val totalNondeductible: Double,
    val openQuestions: Int,
    val byClass: List<TaxClassTotal>,
)

data class TaxOpportunity(
    val id: String,
    val title: String,
    val action: String,
    val reference: String,
    /** close, qualified or not_yet */
    val status: String,
    val estimatedValue: Double,
    val valueNote: String,
    val gap: String,
    val deadline: String?,
)

sealed class ApprovalCard {
    abstract val id: String

    data class Categorize(
        val txn: InboxTransaction,
        val similar: List<InboxTransaction>,
        val confidence: Int,
        val taxLabel: String? = null,
        val deductiblePct: Double? = null,
    ) : ApprovalCard() {
        override val id get() = "cat_" + txn.id
    }

    /** "Who was this meal with?" The answer decides 0%, 50% or 100%. */
    data class MealQuestion(val q: TaxQuestion) : ApprovalCard() {
        override val id get() = "meal_" + q.transactionId
    }

    data class TaxCredit(
        val estimate: TaxCreditEstimate,
        val evidence: List<String>,
    ) : ApprovalCard() {
        override val id get() = "credit_" + estimate.jurisdiction
    }

    data class InvoiceChase(
        val invoice: Invoice,
        val draftEmail: String,
    ) : ApprovalCard() {
        override val id get() = "inv_" + invoice.id
    }
}

data class BooksData(
    val home: HomeSnapshot,
    val runway: Runway?,
    val cards: List<ApprovalCard>,
    val credits: TaxCreditEstimate?,
    val activity: List<AgentActivity>,
    val offline: Boolean,
    val taxSummary: TaxSummary? = null,
    val opportunities: List<TaxOpportunity> = emptyList(),
)
