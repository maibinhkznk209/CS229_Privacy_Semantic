% queries.pl (auto-generated)
:- initialization(main, main).

main :-
  consult('kb/kb.pl'),
  format('Loaded KB.~n', []),
  run_all.

run_all :-
  format('~n[Q1] What information does Google collect when you use its services?~n', []),
  ( findall(X_Q1, (collects(google, X_Q1)), Xs_Q1), Xs_Q1 \= []
  -> format('  Answers: ~w~n', [Xs_Q1])
  ; format('  false / no answers.~n', []) ),
  format('~n[Q2] Why does Google collect this information?~n', []),
  ( findall(Purpose_Q2, (uses_for(google, Purpose_Q2)), Xs_Q2), Xs_Q2 \= []
  -> format('  Answers: ~w~n', [Xs_Q2])
  ; format('  false / no answers.~n', []) ),
  format('~n[Q3] Does the data Google collects depend on your privacy controls?~n', []),
  ( call((varies_by(data_collection, privacy_controls))) -> format('  true.~n', []) ; format('  false / no answers.~n', []) ),
  format('~n[Q4] When you are not signed in, does Google store data under unique identifiers?~n', []),
  ( findall(Purpose_Q4, (stores_under_identifier(google, unique_identifier, not_signed_in, Purpose_Q4)), Xs_Q4), Xs_Q4 \= []
  -> format('  Answers: ~w~n', [Xs_Q4])
  ; format('  false / no answers.~n', []) ),
  format('~n[Q5] What information do you provide when you create a Google Account?~n', []),
  ( call((purpose(google, personal_information, create_or_use_account))) -> format('  true.~n', []) ; format('  false / no answers.~n', []) ),
  format('~n[Q6] Does Google collect content you create or upload (e.g., emails, photos, documents)?~n', []),
  ( findall(X_Q6, (collects_content(google, X_Q6)), Xs_Q6), Xs_Q6 \= []
  -> format('  Answers: ~w~n', [Xs_Q6])
  ; format('  false / no answers.~n', []) ),
  format('~n[Q7] What technologies does Google use to collect technical data (cookies or server logs)?~n', []),
  ( findall(Tech_Q7, (uses_technology(google, Tech_Q7)), Xs_Q7), Xs_Q7 \= []
  -> format('  Answers: ~w~n', [Xs_Q7])
  ; format('  false / no answers.~n', []) ),
  format('~n[Q8] How long does Google keep data, and can users delete or auto-delete it?~n', []),
  ( findall(Policy_Q8, (retains(google, data, Policy_Q8), allows_setting(google, delete), (allows_setting(google, auto_delete) ; true)), Xs_Q8), Xs_Q8 \= []
  -> format('  Answers: ~w~n', [Xs_Q8])
  ; format('  false / no answers.~n', []) ),
  true.
