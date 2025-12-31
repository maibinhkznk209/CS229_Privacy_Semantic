# Question → Prolog Query Mapping

| QID | Question | Prolog Query | Result |
|-----|----------|--------------|--------|
| Q1 | What information does Google collect when you use its services? | `collects(google, X).` | `[information, personal_information]` |
| Q2 | Why does Google collect this information? | `uses_for(google, Purpose).` | `[communicate_with_users, improve_services, maintain_services, personalize_content_ads, protect_from_fraud_abuse_security_risks, provide_services]` |
| Q3 | Does the data Google collects depend on your privacy controls? | `varies_by(data_collection, privacy_controls).` | `true` |
| Q4 | When you are not signed in, does Google store data under unique identifiers? | `stores_under_identifier(google, unique_identifier, not_signed_in, Purpose).` | `[remember_preferences]` |
| Q5 | What information do you provide when you create a Google Account? | `purpose(google, personal_information, create_or_use_account).` | `true` |
| Q6 | Does Google collect content you create or upload (e.g., emails, photos, documents)? | `collects_content(google, X).` | `[user_content]` |
| Q7 | What technologies does Google use to collect technical data (cookies or server logs)? | `uses_technology(google, Tech).` | `[cookies, server_logs]` |
| Q8 | How long does Google keep data, and can users delete or auto-delete it? | `retains(google, data, Policy), allows_setting(google, delete).` | `[retention_policy]` (delete: available, auto_delete: available) |
