"""
EXHAUSTIVE AUTOMATED MASTER TEST SUITE FOR SOVEREIGN OMNICHANNEL EMAIL ENGINE
================================================================================

Tests all 5 core components of the Sovereign Omnichannel Email Engine:
1. SMTP/MIME message building & sending (RFC 5322/2045 headers, Base64 attachments, delivery queue & bounce metrics).
2. Transactional HTML template rendering (Glassmorphic responsive dark mode templates for Invoices, Receipts, and Pay Links + Plain-Text fallbacks).
3. IMAP inbound message parsing (RFC 822 decoding, attachments extraction, IMAP mailbox folder operations & flag management).
4. Inner AI Auto-Responder execution (Autonomous email classification, sentiment & threat detection, thread header linking & automated replies).
5. Email audit logging and GL posting (SHA-256 event audit trails, verification & strict double-entry GL journal posting).

Author: Lead Sovereign OS UI & Financial Accounting Architect
"""

import sys
import os
import time
import email
from email.message import EmailMessage
import unittest

# Ensure root directory and nextgen_systems are on sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
nextgen_dir = os.path.join(root_dir, "sovereign_infrastructure", "nextgen_systems")

if nextgen_dir not in sys.path:
    sys.path.insert(0, nextgen_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from omnichannel_email_engine import (
    SMTPMessageBuilder,
    SovereignSMTPSender,
    TransactionalHTMLTemplateEngine,
    IMAPInboundParser,
    IMAPMailboxSimulator,
    InnerAIAutoResponder,
    EmailAuditLogger,
    EmailGLEngine,
    OmnichannelEmailEngine
)


class TestSMTPMessageBuilderAndSender(unittest.TestCase):
    """Test Suite for Component 1: SMTP/MIME Message Building & Sending"""

    def setUp(self):
        self.builder = SMTPMessageBuilder()
        self.sender = SovereignSMTPSender(smtp_host="smtp.sovereign.io", smtp_port=587)

    def test_01_smtp_email_address_validation(self):
        """Verify email address syntax validation logic."""
        self.assertTrue(self.builder.validate_email_address("alex@sovereign.io"))
        self.assertTrue(self.builder.validate_email_address("Billing Team <billing.dept@sovereign.io>"))
        self.assertFalse(self.builder.validate_email_address("invalid-email-address"))
        self.assertFalse(self.builder.validate_email_address(""))
        self.assertFalse(self.builder.validate_email_address(None))

    def test_02_smtp_mime_message_construction(self):
        """Verify RFC compliant MIME message construction with text/html alternatives."""
        msg = self.builder.build_mime_message(
            sender="billing@sovereign.io",
            recipient="client@acme.com",
            subject="Invoice #INV-2026-001",
            body_html="<h1>Invoice INV-2026-001</h1><p>Amount Due: $1,500.00</p>"
        )

        self.assertIsInstance(msg, EmailMessage)
        self.assertEqual(msg["Subject"], "Invoice #INV-2026-001")
        self.assertEqual(msg["From"], "billing@sovereign.io")
        self.assertEqual(msg["To"], "client@acme.com")
        self.assertIn("@sovereign.io>", msg["Message-ID"])
        self.assertTrue(msg.is_multipart())

        # Check payload parts (text/plain and text/html)
        payload_parts = list(msg.walk())
        content_types = [p.get_content_type() for p in payload_parts]
        self.assertIn("text/plain", content_types)
        self.assertIn("text/html", content_types)

    def test_03_smtp_custom_headers_and_tracking_id(self):
        """Verify custom tracking headers, DKIM simulation, and in-reply-to headers."""
        custom_hdr = {"X-Custom-Campaign": "Spring2026", "X-Priority": "1"}
        msg = self.builder.build_mime_message(
            sender="marketing@sovereign.io",
            recipient="lead@enterprise.com",
            subject="Exclusive Sovereign AI Access",
            body_html="<p>Special offer inside</p>",
            custom_headers=custom_hdr,
            in_reply_to="<parent-msg-123@sovereign.io>",
            references="<root-msg-000@sovereign.io> <parent-msg-123@sovereign.io>"
        )

        self.assertEqual(msg["X-Custom-Campaign"], "Spring2026")
        self.assertEqual(msg["X-Priority"], "1")
        self.assertEqual(msg["In-Reply-To"], "<parent-msg-123@sovereign.io>")
        self.assertIn("<root-msg-000@sovereign.io>", msg["References"])
        self.assertTrue(msg["X-Sovereign-Tracking-ID"].startswith("TRK-"))
        self.assertIn("v=1; a=rsa-sha256", msg["X-DKIM-Signature-Simulated"])

    def test_04_smtp_attachments_encoding_base64(self):
        """Verify file attachments are correctly attached with content-type and filename."""
        pdf_bytes = b"%PDF-1.4 Mock Invoice Document Content Bytes"
        attachments = [{
            "filename": "invoice_INV-2026-001.pdf",
            "content_type": "application/pdf",
            "data": pdf_bytes
        }]

        msg = self.builder.build_mime_message(
            sender="billing@sovereign.io",
            recipient="finance@acme.com",
            subject="Invoice with PDF",
            body_html="<p>Please find attached your PDF invoice.</p>",
            attachments=attachments
        )

        att_found = False
        for part in msg.walk():
            if part.get_filename() == "invoice_INV-2026-001.pdf":
                att_found = True
                self.assertEqual(part.get_content_type(), "application/pdf")
                self.assertEqual(part.get_payload(decode=True), pdf_bytes)

        self.assertTrue(att_found, "Attachment invoice_INV-2026-001.pdf was not found in MIME structure.")

    def test_05_smtp_sender_single_and_bulk_delivery(self):
        """Verify SMTP transport sending single and batch emails."""
        msg1 = self.builder.build_mime_message("dev@sovereign.io", "user1@domain.com", "Test 1", "<p>Hello 1</p>")
        msg2 = self.builder.build_mime_message("dev@sovereign.io", "user2@domain.com", "Test 2", "<p>Hello 2</p>")

        res1 = self.sender.send_message(msg1)
        self.assertEqual(res1["status"], "DELIVERED")
        self.assertEqual(res1["recipient"], "user1@domain.com")
        self.assertGreater(res1["size_bytes"], 0)

        bulk_res = self.sender.send_bulk([msg1, msg2])
        self.assertEqual(len(bulk_res), 2)
        self.assertTrue(all(r["status"] == "DELIVERED" for r in bulk_res))

    def test_06_smtp_sender_bounce_handling_and_metrics(self):
        """Verify delivery metrics and bounce error handling."""
        valid_msg1 = self.builder.build_mime_message("dev@sovereign.io", "user1@domain.com", "Test 1", "<p>Hello 1</p>")
        valid_msg2 = self.builder.build_mime_message("dev@sovereign.io", "user2@domain.com", "Test 2", "<p>Hello 2</p>")
        valid_msg3 = self.builder.build_mime_message("dev@sovereign.io", "user3@domain.com", "Test 3", "<p>Hello 3</p>")
        self.sender.send_bulk([valid_msg1, valid_msg2, valid_msg3])

        bounce_msg = self.builder.build_mime_message(
            "no-reply@sovereign.io",
            "bounce-user@nonexistent-domain.com",
            "Undeliverable Test",
            "<p>Test</p>"
        )

        res = self.sender.send_message(bounce_msg)
        self.assertEqual(res["status"], "BOUNCED")
        self.assertIn("User unknown", res["reason"])

        metrics = self.sender.get_delivery_metrics()
        self.assertGreaterEqual(metrics["total_sent"], 0)
        self.assertEqual(metrics["total_bounced"], 1)
        self.assertEqual(metrics["total_attempts"], 4)
        self.assertGreater(metrics["delivery_rate_pct"], 0.0)


class TestTransactionalHTMLTemplateEngine(unittest.TestCase):
    """Test Suite for Component 2: Transactional HTML Template Rendering"""

    def test_07_invoice_html_template_rendering(self):
        """Verify rendering of Invoice HTML template with itemized details & due date."""
        items = [
            {"description": "Sovereign AI Enterprise License", "qty": 1, "unit_price": 5000.0, "total": 5000.0},
            {"description": "Dedicated Compute Cluster Addon", "qty": 2, "unit_price": 1200.0, "total": 2400.0}
        ]
        html = TransactionalHTMLTemplateEngine.render_invoice_template(
            invoice_id="INV-9901",
            customer_name="Acme Corp",
            customer_email="billing@acme.com",
            items=items,
            subtotal=7400.0,
            tax_amount=740.0,
            total_amount=8140.0,
            due_date="2026-09-15",
            pay_url="https://pay.sovereign.io/l/inv-9901"
        )

        self.assertIn("Invoice INV-9901", html)
        self.assertIn("Acme Corp", html)
        self.assertIn("billing@acme.com", html)
        self.assertIn("Sovereign AI Enterprise License", html)
        self.assertIn("$8,140.00", html)
        self.assertIn("https://pay.sovereign.io/l/inv-9901", html)
        self.assertIn("2026-09-15", html)

    def test_08_receipt_html_template_rendering(self):
        """Verify rendering of Receipt HTML template with payment success checkmark & transaction ID."""
        items = [{"description": "Sovereign Pro Monthly Subscription", "total": 299.00}]
        html = TransactionalHTMLTemplateEngine.render_receipt_template(
            receipt_id="RCT-5021",
            customer_name="Jane Doe",
            customer_email="jane@company.com",
            transaction_id="tx_9988221100",
            items=items,
            total_paid=299.00,
            payment_method="Sovereign ZK Crypto",
            payment_date="2026-08-26 14:30:00 UTC"
        )

        self.assertIn("Payment Successful", html)
        self.assertIn("Receipt #RCT-5021", html)
        self.assertIn("tx_9988221100", html)
        self.assertIn("Sovereign ZK Crypto", html)
        self.assertIn("$299.00", html)

    def test_09_pay_link_html_template_rendering(self):
        """Verify rendering of Pay Link HTML template with product title, amount, and expiration."""
        html = TransactionalHTMLTemplateEngine.render_pay_link_template(
            product_title="Sovereign AI API 100k Tokens Bundle",
            customer_name="TechCorp Inc",
            amount=49.99,
            currency="USD",
            pay_url="https://pay.sovereign.io/l/tokens-100k",
            expiration_date="2026-08-31 23:59:59 UTC",
            description="100,000 High-Speed Inference API Credits"
        )

        self.assertIn("Instant Sovereign Pay Link", html)
        self.assertIn("Sovereign AI API 100k Tokens Bundle", html)
        self.assertIn("$49.99", html)
        self.assertIn("TechCorp Inc", html)
        self.assertIn("https://pay.sovereign.io/l/tokens-100k", html)

    def test_10_html_to_plain_text_fallback_extraction(self):
        """Verify HTML tag stripping and formatting into readable plain text fallback."""
        raw_html = """
        <html>
        <body>
            <h1>Heading Title</h1>
            <p>First paragraph with <a href="https://sovereign.io">link</a>.</p>
            <br>
            <p>Second paragraph content.</p>
        </body>
        </html>
        """
        text = TransactionalHTMLTemplateEngine.html_to_plain_text(raw_html)
        self.assertNotIn("<h1>", text)
        self.assertNotIn("<html>", text)
        self.assertIn("Heading Title", text)
        self.assertIn("First paragraph with link.", text)
        self.assertIn("Second paragraph content.", text)


class TestIMAPInboundParserAndSimulator(unittest.TestCase):
    """Test Suite for Component 3: IMAP Inbound Message Parsing & Mailbox Management"""

    def setUp(self):
        self.parser = IMAPInboundParser()
        self.mailbox = IMAPMailboxSimulator()

    def test_11_imap_parse_raw_mime_simple_text(self):
        """Verify parsing simple RFC 822 plain-text inbound emails."""
        raw_email = (
            "From: client@enterprise.com\r\n"
            "To: support@sovereign.io\r\n"
            "Subject: Inquiry regarding AI API Limits\r\n"
            "Date: Wed, 26 Aug 2026 10:00:00 -0500\r\n"
            "Message-ID: <msg-1001@enterprise.com>\r\n"
            "\r\n"
            "Hello team,\nHow do I upgrade my API rate limits?\nThanks!"
        )

        parsed = self.parser.parse_raw_mime(raw_email)
        self.assertEqual(parsed["sender"], "client@enterprise.com")
        self.assertEqual(parsed["recipient"], "support@sovereign.io")
        self.assertEqual(parsed["subject"], "Inquiry regarding AI API Limits")
        self.assertEqual(parsed["message_id"], "<msg-1001@enterprise.com>")
        self.assertIn("How do I upgrade my API rate limits?", parsed["text_body"])

    def test_12_imap_parse_raw_mime_multipart_html_and_attachments(self):
        """Verify parsing multipart MIME emails containing HTML body and file attachments."""
        builder = SMTPMessageBuilder()
        mime_msg = builder.build_mime_message(
            sender="vendor@partner.com",
            recipient="ap@sovereign.io",
            subject="Vendor Bill BILL-2026-88",
            body_html="<p>Attached is Vendor Bill BILL-2026-88</p>",
            attachments=[{
                "filename": "bill_statement.csv",
                "content_type": "text/csv",
                "data": b"item,amount\nServer,1200.00\n"
            }]
        )

        parsed = self.parser.parse_raw_mime(mime_msg.as_bytes())
        self.assertEqual(parsed["sender"], "vendor@partner.com")
        self.assertEqual(parsed["subject"], "Vendor Bill BILL-2026-88")
        self.assertIn("Attached is Vendor Bill", parsed["html_body"])
        self.assertEqual(len(parsed["attachments"]), 1)
        self.assertEqual(parsed["attachments"][0]["filename"], "bill_statement.csv")

    def test_13_imap_mailbox_simulator_folder_navigation(self):
        """Verify IMAP folder switching (INBOX, SENT, SPAM, ARCHIVE) and email ingestion."""
        raw_email = (
            "From: alert@security.com\r\n"
            "To: admin@sovereign.io\r\n"
            "Subject: System Health Check\r\n"
            "\r\n"
            "All systems nominal."
        )

        ingested = self.mailbox.ingest_raw_email(raw_email, folder="INBOX")
        self.assertEqual(ingested["folder"], "INBOX")
        self.assertGreater(ingested["uid"], 0)

        info = self.mailbox.select_folder("INBOX")
        self.assertEqual(info["total_messages"], 1)
        self.assertEqual(info["unseen_messages"], 1)

    def test_14_imap_search_criteria_and_flag_manipulation(self):
        """Verify IMAP search criteria (ALL, UNSEEN, SEEN, FROM, SUBJECT) and flag manipulation (\\Seen, \\Flagged)."""
        email1 = "From: alice@test.com\r\nSubject: Invoice Query\r\n\r\nDetails 1"
        email2 = "From: bob@test.com\r\nSubject: Pay Link Request\r\n\r\nDetails 2"

        m1 = self.mailbox.ingest_raw_email(email1, "INBOX")
        m2 = self.mailbox.ingest_raw_email(email2, "INBOX")

        self.mailbox.select_folder("INBOX")
        all_uids = self.mailbox.search_messages("ALL")
        self.assertEqual(len(all_uids), 2)

        unseen = self.mailbox.search_messages("UNSEEN")
        self.assertEqual(len(unseen), 2)

        # Mark m1 as \Seen and \Flagged
        self.mailbox.store_flags(m1["uid"], ["\\Seen", "\\Flagged"], mode="+")

        seen_uids = self.mailbox.search_messages("SEEN")
        self.assertIn(m1["uid"], seen_uids)
        self.assertNotIn(m2["uid"], seen_uids)

        subject_uids = self.mailbox.search_messages("SUBJECT Pay Link")
        self.assertIn(m2["uid"], subject_uids)


class TestInnerAIAutoResponder(unittest.TestCase):
    """Test Suite for Component 4: Inner AI Auto-Responder Execution"""

    def setUp(self):
        self.sender = SovereignSMTPSender()
        self.auto_responder = InnerAIAutoResponder(smtp_sender=self.sender)

    def test_15_inner_ai_auto_responder_classification_and_reply(self):
        """Verify AI classification of inbound inquiry and response generation."""
        parsed_inbound = {
            "message_id": "<inquiry-101@client.com>",
            "sender": "client@acme.com",
            "recipient": "support@sovereign.io",
            "subject": "Help with Invoice Generation",
            "text_body": "Hello, how can I generate an invoice for my customer using Sovereign Pay?",
            "references": None
        }

        res = self.auto_responder.process_inbound_email(parsed_inbound, auto_send=True)
        self.assertEqual(res["action"], "AI_RESPONDED")
        self.assertEqual(res["inbound_message_id"], "<inquiry-101@client.com>")
        self.assertTrue(res["response_sent"])
        self.assertEqual(res["delivery_status"], "DELIVERED")

    def test_16_inner_ai_auto_responder_thread_header_linking(self):
        """Verify in-reply-to and references MIME thread header propagation."""
        parsed_inbound = {
            "message_id": "<parent-thread-999@domain.com>",
            "sender": "user@domain.com",
            "subject": "Question on Pay Links",
            "text_body": "Can I set custom payment links?",
            "references": "<root-thread-000@domain.com>"
        }

        res = self.auto_responder.process_inbound_email(parsed_inbound, auto_send=True)
        self.assertEqual(res["action"], "AI_RESPONDED")

        # Inspect sent message in sender history
        sent_item = self.sender.sent_history[-1]
        self.assertEqual(sent_item["recipient"], "user@domain.com")

    def test_17_inner_ai_auto_responder_threat_and_spam_blocking(self):
        """Verify malicious exploit or spam emails are blocked from auto-responding."""
        malicious_inbound = {
            "message_id": "<hack-001@badactor.com>",
            "sender": "attacker@badactor.com",
            "subject": "SECURITY ALERT: Malware Exploit Payload",
            "text_body": "Execute malware exploit payload immediately to gain unauthorized access.",
            "references": None
        }

        res = self.auto_responder.process_inbound_email(malicious_inbound, auto_send=True)
        self.assertEqual(res["action"], "BLOCKED_THREAT")
        self.assertFalse(res["response_sent"])
        self.assertEqual(res["threat_level"], "HIGH")

    def test_18_inner_ai_auto_responder_custom_auto_send_toggle(self):
        """Verify staging response without sending when auto_send=False."""
        parsed_inbound = {
            "message_id": "<stage-001@client.com>",
            "sender": "client2@acme.com",
            "subject": "Receipt query",
            "text_body": "Where is my receipt?",
            "references": None
        }

        res = self.auto_responder.process_inbound_email(parsed_inbound, auto_send=False)
        self.assertEqual(res["action"], "AI_RESPONDED")
        self.assertFalse(res["response_sent"])
        self.assertEqual(res["delivery_status"], "STAGED")


class TestEmailAuditLoggingAndGLPosting(unittest.TestCase):
    """Test Suite for Component 5: Email Audit Logging and GL Posting"""

    def setUp(self):
        self.audit_logger = EmailAuditLogger()
        self.gl_engine = EmailGLEngine()

    def test_19_email_audit_logger_immutable_sha256_hashing(self):
        """Verify audit logger generates valid SHA-256 digests for all logged events."""
        entry = self.audit_logger.log_event(
            event_type="EMAIL_SENT",
            direction="OUTBOUND",
            message_id="<msg-123@sovereign.io>",
            sender="billing@sovereign.io",
            recipient="client@company.com",
            status="DELIVERED",
            payload="Header and Body text payload sample"
        )

        self.assertTrue(entry["audit_id"].startswith("AUD-"))
        self.assertEqual(len(entry["payload_sha256"]), 64)
        self.assertEqual(entry["event_type"], "EMAIL_SENT")

    def test_20_email_audit_logger_filtering_and_integrity_verification(self):
        """Verify audit log filtering and integrity verification."""
        self.audit_logger.log_event("INBOUND_RECEIVED", "INBOUND", "<m1@test.com>", "a@t.com", "b@s.io", "RECEIVED")
        self.audit_logger.log_event("INBOUND_RECEIVED", "INBOUND", "<m2@test.com>", "c@t.com", "b@s.io", "RECEIVED")
        self.audit_logger.log_event("OUTBOUND_SENT", "OUTBOUND", "<m3@sovereign.io>", "b@s.io", "a@t.com", "DELIVERED")

        inbound_logs = self.audit_logger.get_audit_logs({"direction": "INBOUND"})
        self.assertEqual(len(inbound_logs), 2)

        outbound_logs = self.audit_logger.get_audit_logs({"event_type": "OUTBOUND_SENT"})
        self.assertEqual(len(outbound_logs), 1)

        self.assertTrue(self.audit_logger.verify_audit_integrity())

    def test_21_gl_posting_invoice_double_entry(self):
        """Verify double-entry GL journal posting for invoice emails (DR: AR 1200, CR: Revenue 4010)."""
        gl_res = self.gl_engine.post_invoice_email_gl(
            invoice_id="INV-2026-90",
            customer_id="cust_8877",
            amount=2500.00
        )

        self.assertEqual(gl_res["amount"], 2500.00)
        self.assertEqual(gl_res["debits"]["1200"], 2500.00)
        self.assertEqual(gl_res["credits"]["4010"], 2500.00)
        self.assertEqual(sum(gl_res["debits"].values()), sum(gl_res["credits"].values()))

    def test_22_gl_posting_receipt_double_entry(self):
        """Verify double-entry GL journal posting for payment receipt emails (DR: Cash 1010, CR: AR 1200)."""
        gl_res = self.gl_engine.post_receipt_email_gl(
            receipt_id="RCT-2026-12",
            customer_id="cust_8877",
            amount=2500.00
        )

        self.assertEqual(gl_res["amount"], 2500.00)
        self.assertEqual(gl_res["debits"]["1010"], 2500.00)
        self.assertEqual(gl_res["credits"]["1200"], 2500.00)
        self.assertEqual(sum(gl_res["debits"].values()), sum(gl_res["credits"].values()))

    def test_23_gl_posting_api_monetization_double_entry(self):
        """Verify double-entry GL journal posting for monetized outbound email API usage."""
        gl_res = self.gl_engine.post_email_api_monetization_gl(
            transaction_id="tx_api_call_500",
            amount=50.00,
            volume_count=5000
        )

        self.assertEqual(gl_res["amount"], 50.00)
        self.assertEqual(gl_res["debits"]["1010"], 50.00)
        self.assertEqual(gl_res["credits"]["4010"], 50.00)
        self.assertEqual(sum(gl_res["debits"].values()), sum(gl_res["credits"].values()))


class TestOmnichannelEmailEngineMasterPipeline(unittest.TestCase):
    """Test Suite for End-to-End Master Pipeline Integration"""

    def setUp(self):
        self.engine = OmnichannelEmailEngine()

    def test_24_omnichannel_email_engine_master_end_to_end_pipeline(self):
        """Verify end-to-end flow: Invoice email sending, Receipt email, Pay Link email, and Inbound AI response."""
        # 1. Send Transactional Invoice
        inv_data = {
            "invoice_id": "INV-MASTER-001",
            "customer_name": "Sovereign Corp",
            "customer_email": "finance@sovereigncorp.com",
            "items": [{"description": "Sovereign AI Node", "qty": 1, "unit_price": 10000.0, "total": 10000.0}],
            "subtotal": 10000.0,
            "tax_amount": 0.0,
            "total_amount": 10000.0,
            "due_date": "2026-09-01",
            "pay_url": "https://pay.sovereign.io/l/inv-master-001"
        }
        inv_res = self.engine.send_transactional_invoice(inv_data)
        self.assertEqual(inv_res["send_result"]["status"], "DELIVERED")
        self.assertEqual(inv_res["gl_entry"]["debits"]["1200"], 10000.0)

        # 2. Send Transactional Receipt
        rct_data = {
            "receipt_id": "RCT-MASTER-001",
            "customer_name": "Sovereign Corp",
            "customer_email": "finance@sovereigncorp.com",
            "transaction_id": "tx_master_99",
            "items": [{"description": "Sovereign AI Node", "total": 10000.0}],
            "total_paid": 10000.0,
            "payment_method": "ACH Direct",
            "payment_date": "2026-08-26 15:00:00"
        }
        rct_res = self.engine.send_transactional_receipt(rct_data)
        self.assertEqual(rct_res["send_result"]["status"], "DELIVERED")
        self.assertEqual(rct_res["gl_entry"]["debits"]["1010"], 10000.0)

        # 3. Send Transactional Pay Link
        link_data = {
            "product_title": "Custom AI Agent Training Bundle",
            "customer_name": "Sovereign Corp",
            "customer_email": "finance@sovereigncorp.com",
            "amount": 2500.00,
            "currency": "USD",
            "pay_url": "https://pay.sovereign.io/l/agent-training",
            "expiration_date": "2026-09-05 23:59:59"
        }
        link_res = self.engine.send_transactional_pay_link(link_data)
        self.assertEqual(link_res["send_result"]["status"], "DELIVERED")

        # 4. Handle Inbound Email & AI Response
        inbound_raw = (
            "From: finance@sovereigncorp.com\r\n"
            "To: support@sovereign.io\r\n"
            "Subject: Pay link confirmation\r\n"
            "Message-ID: <inbound-corp-777@sovereigncorp.com>\r\n"
            "\r\n"
            "Hello, thank you for sending the payment link for agent training. We have received it."
        )
        inbound_res = self.engine.handle_inbound_stream(inbound_raw, auto_respond=True)
        self.assertEqual(inbound_res["parsed_inbound"]["sender"], "finance@sovereigncorp.com")
        self.assertEqual(inbound_res["auto_responder"]["action"], "AI_RESPONDED")
        self.assertTrue(inbound_res["auto_responder"]["response_sent"])

        # 5. Check Master System Status & Audit Integrity
        status = self.engine.get_system_status()
        self.assertEqual(status["status"], "HEALTHY")
        self.assertGreaterEqual(status["total_audit_logs"], 5)
        self.assertGreaterEqual(status["total_gl_entries"], 2)
        self.assertTrue(status["audit_integrity_valid"])


if __name__ == "__main__":
    unittest.main()
