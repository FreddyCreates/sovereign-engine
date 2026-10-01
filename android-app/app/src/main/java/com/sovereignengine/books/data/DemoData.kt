package com.sovereignengine.books.data

/**
 * Sample data used when the books API is unreachable or demo mode is on.
 * It mirrors the founder story: three cards, ninety seconds, done.
 */
object DemoData {

    private val similar = listOf(
        InboxTransaction("txn_s1", "2026-08-30", "Notion Labs", "Notion Labs", 4200.0, false, "Software", "Business Checking", "4521"),
        InboxTransaction("txn_s2", "2026-07-30", "Notion Labs", "Notion Labs", 4200.0, false, "Software", "Business Checking", "4521"),
        InboxTransaction("txn_s3", "2026-06-30", "Notion Labs", "Notion Labs", 3900.0, false, "Software", "Business Checking", "4521"),
    )

    val credits = TaxCreditEstimate(
        jurisdiction = "US_CA",
        cloudQre = 18_400.0,
        payrollQre = 61_000.0,
        totalQre = 79_400.0,
        federalCredit = 11_116.0,
        stateCredit = 11_910.0,
        totalCredits = 23_026.0,
        amortizationDeduction = 15_880.0,
        references = listOf(
            "IRC Section 41: Credit for increasing research activities",
            "IRC Section 174: Amortization of research and experimental expenditures",
            "California R&D Credit (Revenue and Taxation Code 23609)",
        ),
    )

    val mealQuestion = TaxQuestion(
        transactionId = "txn_demo_meal",
        question = "Who was this meal with?",
        answers = listOf(
            TaxAnswer("client", "Client or prospect was there", 0.5),
            TaxAnswer("employee", "One or a few employees", 0.5),
            TaxAnswer("all_employees", "Whole company event", 1.0),
            TaxAnswer("traveling", "I was traveling for work", 0.5),
            TaxAnswer("office_provided", "Food for the office", 0.0),
            TaxAnswer("solo", "Just me, in town", 0.0),
            TaxAnswer("personal", "Personal", 0.0),
        ),
        merchant = "Bistro 42",
        date = "2026-09-30",
        amount = 186.40,
        currentDeductiblePct = 0.5,
    )

    val taxSummary = TaxSummary(
        taxYear = 2026,
        totalSpent = 38_420.0,
        totalDeductible = 33_110.0,
        totalNondeductible = 5_310.0,
        openQuestions = 1,
        byClass = listOf(
            TaxClassTotal("CLOUD_100", "Cloud hosting and compute", 1.0, 9, 18_400.0, 18_400.0),
            TaxClassTotal("SOFTWARE_100", "Software and subscriptions", 1.0, 14, 9_860.0, 9_860.0),
            TaxClassTotal("MEAL_BUSINESS_50", "Business meal (client or employee present)", 0.5, 11, 4_120.0, 2_060.0),
            TaxClassTotal("TRAVEL_100", "Travel: airfare, rail, rideshare, car rental", 1.0, 6, 2_790.0, 2_790.0),
            TaxClassTotal("ENTERTAINMENT_0", "Entertainment (tickets, golf, club dues)", 0.0, 2, 1_250.0, 0.0),
            TaxClassTotal("MEAL_SOLO_0", "Solo meal, not traveling", 0.0, 8, 2_000.0, 0.0),
        ),
    )

    val opportunities = listOf(
        TaxOpportunity("company_event_100", "Hold a company-wide event", "Your next team dinner or offsite: invite the whole team and it is 100% deductible instead of 50%. Hold it before December 31 and keep the invite list.", "IRC 274(e)(4), 274(n)(2)(A)", "close", 494.0, "Tax saved on a \$4,120 event versus the same amount as 50% meals, at 24%", "You have \$4,120 of 50% meals this year and \$0 of 100% events.", "2026-12-31"),
        TaxOpportunity("separate_meals_from_entertainment", "Separate food from entertainment", "Tickets and golf are not deductible, but food bought separately at the event is a 50% meal. Ask vendors to invoice food on its own line.", "IRC 274(a); Reg. 1.274-11", "close", 45.0, "Assumes 30% of the spend was food", "\$1,250 of entertainment is currently 0% deductible.", null),
        TaxOpportunity("research_credit_41", "Claim the research credit", "Track engineering hours by project and keep commit history. File Form 6765 with the return. Businesses under five years of revenue can take up to \$500,000 against payroll tax on Form 8974.", "IRC 41; IRC 41(h) payroll offset", "qualified", 11_116.0, "Federal credit at the 14% alternative simplified rate", "Qualified research expenses so far: \$79,400.", null),
        TaxOpportunity("section_179", "Expense equipment in year one", "Buy and place in service the equipment you already need before December 31 and elect Section 179 on Form 4562.", "IRC 179; IRC 168(k)", "close", 1_200.0, "Tax on the amount deducted this year rather than depreciated", "No equipment over the threshold yet.", "2026-12-31"),
        TaxOpportunity("retirement_startup_credit", "Start a retirement plan", "Open a 401(k) or SIMPLE IRA. Employers with up to 100 employees get a credit for startup costs for three years, plus \$500 a year for auto-enrollment.", "IRC 45E, 45T", "close", 5_500.0, "Maximum first-year credit", "No retirement plan provider seen in payroll vendors.", null),
    )

    val cards: List<ApprovalCard> = listOf(
        ApprovalCard.Categorize(
            txn = InboxTransaction("txn_demo_1", "2026-09-30", "Notion Labs", "Notion Labs", 4200.0, false, "Software", "Business Checking", "4521"),
            similar = similar,
            confidence = 74,
            taxLabel = "Software and subscriptions",
            deductiblePct = 1.0,
        ),
        ApprovalCard.MealQuestion(mealQuestion),
        ApprovalCard.TaxCredit(
            estimate = credits,
            evidence = listOf(
                "412 commits across 3 engineering projects this quarter",
                "Payroll: 4 engineers, 61,000 USD allocated to qualified research",
                "Cloud compute: 18,400 USD on build and test infrastructure",
            ),
        ),
        ApprovalCard.InvoiceChase(
            invoice = Invoice("inv_demo_1", "Harbor Logistics", 12_500.0, "open", "2026-07-02", 90),
            draftEmail = "Hi Dana,\n\nInvoice INV-0412 for 12,500 USD was due on July 2 and is now 90 days past due. Could you let us know when we can expect payment, or if anything is holding it up?\n\nThanks,\nSovereign Demo Co",
        ),
    )

    val data = BooksData(
        home = HomeSnapshot("Sovereign Demo Co", 24_180.42, cards.size, false, "offline"),
        runway = Runway(4.84, 24_180.42, "Runway about 4.8 months at 5,000 USD per month burn"),
        cards = cards,
        credits = credits,
        activity = listOf(
            AgentActivity("07:02", "Categorized 11 transactions with high confidence"),
            AgentActivity("07:02", "Posted 11 journal entries; trial balance OK"),
            AgentActivity("07:05", "Found 61,000 USD of payroll that qualifies for Section 41"),
            AgentActivity("07:06", "Drafted a follow-up for one invoice 90 days overdue"),
        ),
        offline = true,
        taxSummary = taxSummary,
        opportunities = opportunities,
    )
}
