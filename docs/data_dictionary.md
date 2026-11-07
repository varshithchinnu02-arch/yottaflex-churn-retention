# Data dictionary and relationship summary

PK = primary key; FK = foreign key. Dates are ISO dates; monetary amounts are USD; usage is synthetic units/month.

| Entity | Key fields | Required / validation |
|---|---|---|
| Customer | customer_id PK (`CUS-000001`), signup_date, region, acquisition_channel, customer_segment, seasonality_type | All required; region North/South/East/West; segment Consumer/Small Business/Enterprise |
| Subscription | subscription_id PK (`SUB-CUS-000001-01`), customer_id FK, product_cohort, plan_name, monthly_price, start_date, status, billing_cycle | Required; plan Basic/Standard/Premium; price >= 0; lifecycle active/churned |
| UsageSnapshot | snapshot_id PK (`SNAP-<subscription-id>-YYYY-MM`), subscription_id FK, customer_id FK, snapshot_date, usage_units, active_days | Required; usage >= 0; one monthly snapshot per subscription |
| BillingEvent | billing_event_id PK, subscription_id FK, customer_id FK, billing_date, amount_due, overdue_amount, payment_status | Required; amounts >= 0; status paid/late |
| SupportCase | support_case_id PK, customer_id FK, subscription_id FK, opened_date, case_type, priority, case_status | Required; types Billing/Technical/Cancellation/Product; priority Low/Medium/High |
| Offer | offer_id PK (`OFF-2026-000001`), offer_name, discount_rate, duration_months, max_cost, active | Required; discount 0–1; duration > 0; max_cost >= 0 |
| EligibilityRule | eligibility_rule_id PK, rule_name, min_churn_probability, min_margin, max_offer_cost, active | Required; probability 0–1; margin/cost in USD |
| CampaignContact | campaign_contact_id PK, customer_id FK, group_name, offer_id FK optional, contact_date | Treatment/control; offer required for treatment, null for control |
| ChurnOutcome | customer_id PK/FK, churn_label, prediction_date, horizon_months | 1:1 with prediction cohort; label 0/1 |
| RetentionOutcome | customer_id PK/FK, retained_6m, retention_revenue, offer_cost, net_value | 1:1 with campaign cohort; retained 0/1 |

Relationships: Customer 1:N Subscription; Subscription 1:N UsageSnapshot, BillingEvent and SupportCase; Customer 1:N SupportCase; Offer 1:N CampaignContact; Customer 1:1 ChurnOutcome and RetentionOutcome. In this starter generator each customer has one subscription. Production N:M customer-to-offer attribution should use a CampaignOffer bridge; this prototype intentionally assigns at most one offer per eligible treatment customer.

Prediction date is 2025-12-01. Features use records strictly before that date. Label horizon is 2026-01-01 through 2026-06-30. Customers who churned before prediction date are excluded. Ground truth and exception register are separate from features. ChurnOutcome.csv stores the cohort labels separately.
