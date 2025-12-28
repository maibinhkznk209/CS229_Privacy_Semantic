% validator.pl
% Validate whether a logical formula is well-formed under a chosen vocabulary.
%
% Usage in SWI-Prolog:
%   ?- [kb/vocab, kb/validator].
%   ?- valid_formula(collects(google, information)).
%   true.
%   ?- valid_formula(foo(bar)).
%   false.

:- module(validator, [
    allowed_pred/2,
    valid_formula/1,
    valid_term/1
]).



% --- Option (1): manual allowed predicates ---
allowed_pred(collects, 2).
allowed_pred(collects_content, 2).
allowed_pred(collects_tech_data, 2).
allowed_pred(uses_technology, 2).
allowed_pred(uses_for, 2).
allowed_pred(purpose, 3).
allowed_pred(varies_by, 2).
allowed_pred(stores_under_identifier, 4).
allowed_pred(retains, 3).
allowed_pred(allows_setting, 2).
allowed_pred(may_keep_longer_for, 3).

% --- Term validation (very lightweight) ---
% Accept atoms (constants) and variables.
valid_term(Term) :- var(Term), !.
valid_term(Term) :- atom(Term), !.
valid_term(Term) :-
    compound(Term),
    functor(Term, _F, _A).  % allow nested terms if you need them

% --- Formula validation ---
% Atomic predicate
valid_formula(Formula) :-
    compound(Formula),
    functor(Formula, Pred, Arity),
    allowed_pred(Pred, Arity),
    Formula =.. [_|Args],
    valid_terms(Args),
    !.

% Logical connectives (optional)
valid_formula(and(F1, F2)) :- valid_formula(F1), valid_formula(F2).
valid_formula(or(F1, F2))  :- valid_formula(F1), valid_formula(F2).
valid_formula(not(F))      :- valid_formula(F).

% Quantifiers (optional)
valid_formula(forall(_Var, F)) :- valid_formula(F).
valid_formula(exists(_Var, F)) :- valid_formula(F).

valid_terms([]).
valid_terms([H|T]) :- valid_term(H), valid_terms(T).
