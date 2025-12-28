# Word Sense Disambiguation (WSD) Module

## 📁 Cấu trúc thư mục

```
wsd/
├── data/
│   ├── reference_annotations.csv   # Ground truth (82 từ từ Privacy Policy)
│   └── semcor_instances.jsonl      # Training data từ SemCor (73MB)
│
├── models/
│   └── bert_semcor_model.pkl       # BERT+SVM trained model (48MB)
│
├── results/
│   ├── mfs_eval.json               # MFS evaluation results
│   ├── bert_semcor_eval.json       # BERT+SVM evaluation results
│   ├── predictions_mfs.json        # MFS predictions
│   └── predictions_bert_semcor.json # BERT predictions
│
├── prepare_semcor.py    # Bước 1: Chuẩn bị SemCor data
├── train_bert.py        # Bước 2: Train BERT+SVM trên SemCor
├── baseline_mfs.py      # Bước 3: Eval MFS baseline
├── predict_and_eval.py  # Bước 4: Eval BERT+SVM
│
└── README.md
```

## 🚀 Cách chạy

### 1. Chuẩn bị môi trường
```bash
pip install nltk scikit-learn joblib transformers torch
python -c "import nltk; nltk.download('wordnet'); nltk.download('semcor')"
```

### 2. Chuẩn bị dữ liệu SemCor (chỉ chạy 1 lần)
```bash
python wsd/prepare_semcor.py
```

### 3. Train BERT+SVM (chỉ chạy 1 lần, hoặc dùng model có sẵn)
```bash
python wsd/train_bert.py
```

### 4. Chạy đánh giá
```bash
# MFS Baseline
python wsd/baseline_mfs.py

# BERT + SVM
python wsd/predict_and_eval.py
```

## 📊 Kết quả

| Model | Accuracy | Training | Test Data |
|-------|----------|----------|-----------|
| **MFS Baseline** | ~77% | Zero-shot | reference_annotations.csv |
| **BERT + SVM** | ~69% | SemCor | reference_annotations.csv |

## 📝 Ghi chú

- **MFS (Most Frequent Sense)**: Sử dụng nghĩa đầu tiên từ WordNet (zero-shot, không cần train)
- **BERT + SVM**: Dùng BERT embeddings làm features, train SVM classifier trên SemCor
- Cả 2 models đều đánh giá trên cùng tập test: `reference_annotations.csv` (82 từ từ đoạn văn Privacy Policy)
