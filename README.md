## Privacy Policy Pipeline

This folder contains code for the remaining steps after choosing the paragraph + queries.

## Files (overview)
- `backend/build_vocab.py` → generates `out/vocabulary.json`, `out/vocabulary.md`, `out/vocab.pl`
- `kb/validator.pl` → Prolog validator: `valid_formula/1`
- `backend/build_kb.py` → builds `kb/kb.pl` and `kb/kb_fol.md` (heuristic translation)
- `backend/generate_queries.py` → builds `results/queries.pl` and mapping table
- `wsd/*` → WSD: SemCor instances, MFS baseline, per-lemma classifier, in-domain predictions
- `augment/wordnet_augment.py` → WordNet augmentationinto `kb/kb_aug.pl`
- `backend/run_all.py` → runs quickly

## Run core steps
```bash
python backend/run_all.py
```

## Run queries in SWI-Prolog
```bash
swipl -q -f results/queries.pl
```

## WSD 
Install:
```bash
pip install nltk scikit-learn joblib
```

Download NLTK data:
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger'); nltk.download('wordnet'); nltk.download('omw-1.4'); nltk.download('semcor')"
```

Run:
```bash
python wsd/prepare_semcor.py
python wsd/baseline_mfs.py
python wsd/train_per_lemma.py
python wsd/predict_in_domain.py
```

## WordNet augmentation
```bash
python augment/wordnet_augment.py
```