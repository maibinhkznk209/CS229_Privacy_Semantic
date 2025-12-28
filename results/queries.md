Question → Prolog Query Mapping

| QID | Question | Prolog Query | Answer shape |
|---|---|---|---|
| Q1 | What information does Google collect when you use its services? | `collects(google, X).` | X (all collected data types) |
| Q2 | Why does Google collect this information? | `uses_for(google, Purpose).` | Purpose (all purposes) |
| Q3 | Does the data Google collects depend on your privacy controls? | `varies_by(data_collection, privacy_controls).` | true/false |
| Q4 | When you are not signed in, does Google store data under unique identifiers? | `stores_under_identifier(google, unique_identifier, not_signed_in, Purpose).` | Purpose |
| Q5 | What information do you provide when you create a Google Account? | `purpose(google, personal_information, create_or_use_account).` | true/false |
| Q6 | Does Google collect content you create or upload (e.g., emails, photos, documents)? | `collects_content(google, X).` | X (content type) |
| Q7 | What technologies does Google use to collect technical data (cookies or server logs)? | `uses_technology(google, Tech).` | Tech |
| Q8 | How long does Google keep data, and can users delete or auto-delete it? | `retains(google, data, Policy), allows_setting(google, delete), (allows_setting(google, auto_delete) ; true).` | Policy + delete/auto-delete availability |
