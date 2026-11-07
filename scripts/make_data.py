"""Generates the synthetic Northwind Payments dataset (already committed in data/)."""
import json, pathlib
D = pathlib.Path(__file__).resolve().parent.parent / "data"

def rec(i, date, typ, text): return {"id": i, "date": date, "type": typ, "text": text}

controls = [rec(i, "2025-01-15", "control", t) for i, t in [
 ("C-01","Control CC6.1 Authentication: all staff must authenticate with a password meeting policy plus MFA. Owner: Meera Iyer (IT Security). Evidence: identity provider configuration screenshots."),
 ("C-02","Control CC6.2 Quarterly access review: production and finance database user access must be reviewed every quarter and signed off. Owner: Rahul Menon (IT Ops). Evidence: reviewer sign-off plus timestamped console screenshots."),
 ("C-03","Control CC6.3 Offboarding: access of departed employees must be removed within 24 hours. Owner: Anita Desai (HR). Evidence: HRIS and identity provider ticket trail."),
 ("C-04","Control CC9.2 Vendor access review: every third-party vendor with access to production or payment systems must be reviewed. Owner: Vikram Shah (Vendor Management). Evidence: vendor list with approval status."),
 ("C-05","Control A1.2 Backups: production databases are backed up daily with 35-day retention. Owner: Rahul Menon. Evidence: backup job reports."),
 ("C-06","Control A1.3 Backup restore test: a full restore of the production database must be tested at least every 6 months. Owner: Rahul Menon. Evidence: restore log plus verification screenshot."),
 ("C-07","Control CC6.7 Device encryption: all company laptops must have full-disk encryption. Owner: Meera Iyer. Evidence: MDM compliance screenshots."),
 ("C-08","Control CC7.1 Vulnerability management: infrastructure is scanned monthly and critical issues fixed within 14 days. Owner: Meera Iyer."),
 ("C-09","Control CC7.2 Incident response: a tabletop exercise is run once a year. Owner: Sana Qureshi (Engineering Manager)."),
 ("C-10","Control CC8.1 Change management: every production change needs an approved pull request. Owner: Sana Qureshi."),
 ("C-11","Control CC1.4 Security awareness: all staff complete training annually, target 95% completion. Owner: Anita Desai."),
 ("C-12","Control CC3.2 Risk assessment: a formal risk assessment is performed annually. Owner: Meera Iyer."),
 ("C-13","Control CC6.6 Firewall review: firewall rules are reviewed every 6 months. Owner: Rahul Menon."),
 ("C-14","Control CC7.3 Logging: security logs are retained for 12 months. Owner: Meera Iyer."),
 ("C-15","Control P6.1 Data deletion: customer data is deleted within 30 days after contract end. Owner: Sana Qureshi."),
 ("C-16","Control CC5.3 Policy review: every security policy is reviewed annually. Owner: Meera Iyer."),
]]

findings = [
 rec("F-2024-01","2024-10-18","audit finding","2024 SOC 2 audit (lead auditor Priya Nair, Larkspur Assurance), severity High: the quarterly user access review for the finance database was not performed during 2024."),
 rec("F-2024-02","2024-10-18","audit finding","2024 SOC 2 audit (Priya Nair), severity High: no vendor access review was performed for third-party payment processor integrations (control C-04)."),
 rec("F-2024-03","2024-10-18","audit finding","2024 SOC 2 audit (Priya Nair), severity Medium: offboarding access removal took up to 6 days for 4 of 25 sampled leavers."),
 rec("F-2025-01","2025-10-21","audit finding","2025 SOC 2 audit (Priya Nair), severity High, REPEAT FINDING: vendor access review again not performed for 3 payment processor integrations onboarded after the Feb 2025 one-time review. This is the second consecutive year the vendor access review control failed (see F-2024-02)."),
 rec("F-2025-02","2025-10-21","audit finding","2025 SOC 2 audit (Priya Nair), severity High: the auditor could not verify remediation of F-2024-01. Ticket REM-14 was marked Done but no evidence was provided. Carried forward as an open item."),
 rec("F-2025-03","2025-10-21","audit finding","2025 SOC 2 audit (Priya Nair), severity Medium: laptop encryption evidence was supplied as a CSV export from the MDM and was rejected. Priya Nair requires timestamped screenshots taken directly from the MDM console."),
 rec("F-2025-04","2025-10-21","audit finding","2025 SOC 2 audit (Priya Nair), severity Low: security awareness training completion was 91% against a 95% target."),
 rec("F-2025-05","2025-10-21","audit finding","2025 SOC 2 audit (Priya Nair), severity Low: the semiannual firewall rule review was completed 2 weeks late."),
 rec("A-01","2025-10-21","auditor note","Auditor profile: Priya Nair (Larkspur Assurance) led the 2024 and 2025 audits. She accepts only timestamped screenshots taken directly from source consoles, rejects CSV or spreadsheet exports, and samples 25 users or records per control."),
]

tickets = [
 rec("REM-09","2025-03-04","remediation ticket","Ticket REM-09 (offboarding delays, F-2024-03), owner Anita Desai. Closed 2025-03-04 with evidence: HRIS to identity provider auto-sync screenshots attached."),
 rec("REM-11","2025-02-28","remediation ticket","Ticket REM-11 (vendor access review, F-2024-02), owner Vikram Shah. Closed 2025-02-28 with evidence: a spreadsheet showing a one-time review of 6 vendors. No recurring schedule was set up."),
 rec("REM-14","2025-05-20","remediation ticket","Ticket REM-14 (finance database quarterly access review, F-2024-01), owner Rahul Menon. Closed 2025-05-20 with status Done. The evidence field is empty: no files were attached."),
 rec("REM-17","2025-11-20","remediation ticket","Ticket REM-17 (laptop encryption evidence, F-2025-03), owner Meera Iyer. Closed 2025-11-20 after timestamped MDM screenshots were accepted by the auditor."),
 rec("REM-18","2026-03-15","remediation ticket","Ticket REM-18 (repeat vendor access review finding, F-2025-01), owner Vikram Shah. Status In Progress, last updated 2026-03-15. No recurring vendor review schedule has been evidenced."),
 rec("REM-19","2025-10-28","remediation ticket","Ticket REM-19 (unverifiable finance database access review, F-2025-02), owner Rahul Menon. Status Open since 2025-10-28. Plan: re-perform and evidence the quarterly reviews."),
 rec("REM-21","2025-12-02","remediation ticket","Ticket REM-21 (late firewall review, F-2025-05), owner Rahul Menon. Closed 2025-12-02 with evidence: signed review log and rule export screenshots."),
 rec("REM-22","2026-01-30","remediation ticket","Ticket REM-22 (training completion, F-2025-04), owner Anita Desai. Closed 2026-01-30 with LMS screenshot showing 97% completion."),
 rec("REM-23","2026-08-14","remediation ticket","Ticket REM-23 (password policy v4.0 rollout), owner Meera Iyer. Identity provider configuration updated 2026-08-14 (14 character minimum, MFA for all production access). Sub-task 're-collect password and MFA evidence dated after 2026-08-01' is still Open."),
]

policies = [
 rec("P-01","2025-02-01","policy change","Access Control Policy v3.1 took effect 2025-02-01: quarterly access reviews must explicitly include the finance database."),
 rec("P-02","2025-09-15","policy change","Data Retention Policy v2.0 took effect 2025-09-15: customer data must be deleted 30 days after contract end."),
 rec("P-03","2026-01-10","policy change","Incident Response Policy v2.2 took effect 2026-01-10: new severity matrix with a 1-hour response target for Sev-1."),
 rec("P-04","2026-08-01","policy change","Password and Authentication Policy v4.0 took effect 2026-08-01: minimum password length raised from 12 to 14 characters and MFA is mandatory for all production access including break-glass accounts. Evidence collected before 2026-08-01 no longer demonstrates compliance with control CC6.1."),
 rec("P-05","2026-09-20","policy change","Vendor Management Policy v2.0 took effect 2026-09-20: vendor access reviews are now quarterly (previously annual) for payment-critical vendors."),
]

tests = [
 rec("CT-01","2025-06-12","control test","Control C-06 backup restore test on 2025-06-12: Pass. Restore log attached."),
 rec("CT-02","2025-12-10","control test","Control C-06 backup restore test on 2025-12-10: Pass. This is the most recent restore test on record; none has been logged since."),
 rec("CT-03","2026-04-08","control test","Control C-02 Q1 2026 finance database access review on 2026-04-08: Pass, timestamped screenshots attached."),
 rec("CT-04","2026-07-09","control test","Control C-02 Q2 2026 finance database access review on 2026-07-09: Pass, timestamped screenshots attached."),
 rec("CT-05","2026-10-15","control test","Control C-02 Q3 2026 finance database access review was due 2026-10-15: NOT PERFORMED, no record exists."),
 rec("CT-06","2026-03-20","control test","Control C-04 vendor access review on 2026-03-20: Partial. 9 of 11 vendors reviewed; 2 payment processors missing."),
 rec("CT-07","2026-09-30","control test","Control C-07 laptop encryption check on 2026-09-30: Pass, timestamped MDM screenshots attached."),
 rec("CT-08","2026-10-31","control test","Control C-08 monthly vulnerability scan on 2026-10-31: Pass. All critical issues fixed within 14 days."),
 rec("CT-09","2026-09-18","control test","Control C-03 offboarding sample on 2026-09-18: Pass. 25 of 25 leavers had access removed within 24 hours."),
]

slack = [
 rec("S-01","2025-05-20","slack message","#it-ops, Rahul Menon, 2025-05-20: closing REM-14, access review is done, will upload the evidence later, auditors are not here until October."),
 rec("S-02","2025-06-02","slack message","#it-ops, Meera Iyer, 2025-06-02: @Rahul REM-14 still has no attachment? No reply followed."),
 rec("S-03","2025-10-23","slack message","#compliance, Vikram Shah, 2025-10-23: Priya says the vendor review is a repeat finding. Two years in a row, leadership will not be happy."),
 rec("S-04","2025-10-24","slack message","#compliance, Meera Iyer, 2025-10-24: Priya rejected our CSV export for encryption. She wants timestamped screenshots from the MDM console, same as she asked for last year."),
 rec("S-05","2026-06-15","slack message","#it-ops, Rahul Menon, 2026-06-15: backup restore test is due but the staging cluster is being rebuilt, pushing it to next month."),
 rec("S-06","2026-08-03","slack message","#compliance, Meera Iyer, 2026-08-03: Password policy v4.0 is live. Heads up, all MFA and password evidence from before Aug 1 is stale for the audit."),
 rec("S-07","2026-09-22","slack message","#compliance, Vikram Shah, 2026-09-22: New vendor policy means quarterly reviews for payment vendors. We have not done a full one since March."),
 rec("S-08","2026-10-16","slack message","#it-ops, Rahul Menon, 2026-10-16: Q3 finance DB access review slipped, will do it after the release."),
 rec("S-09","2026-11-02","slack message","#compliance, Anita Desai, 2026-11-02: Offboarding sample looks clean, evidence uploaded with screenshots."),
]

for name, data in [("controls",controls),("audit_findings",findings),("remediation_tickets",tickets),
                   ("policy_changes",policies),("control_tests",tests),("slack_snippets",slack)]:
    (D/f"{name}.json").write_text(json.dumps(data, indent=2))
    print(name, len(data))
