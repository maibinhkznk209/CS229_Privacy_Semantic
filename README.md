# CS229 - Ngữ Nghĩa Học Tính Toán
## Đồ Án 2: Gán Nhãn Nghĩa Của Từ (Word Sense Disambiguation)

> **Môn học:** CS229 - Ngữ Nghĩa Học Tính Toán  
> **Trường:** ĐH Công Nghệ Thông Tin, ĐHQG-HCM

---

## 📋 Mục Lục

- [Giới Thiệu](#-giới-thiệu)
- [Cấu Trúc Dự Án](#-cấu-trúc-dự-án)
- [Cài Đặt](#-cài-đặt)
- [Chạy Web Demo](#-chạy-web-demo)
- [WSD Models](#-wsd-models)
- [Knowledge Base](#-knowledge-base)
- [Kết Quả](#-kết-quả)

---

## 🎯 Giới Thiệu

Dự án thực hiện các yêu cầu của Đồ Án 2:

1. **Giới thiệu đồ án**: Đoạn văn bản Privacy Policy của Google
2. **Huấn luyện mô hình WSD**: MFS Baseline và BERT + SVM
3. **Biểu diễn tri thức**: Prolog Knowledge Base và FOL
4. **Truy vấn tri thức**: 8 câu truy vấn Prolog
5. **WordNet Augmentation**: Bổ sung synonym và hypernym từ WordNet

---

## 📁 Cấu Trúc Dự Án

```
CS229_Privacy_Semantic/
│
├── data/                          # Dữ liệu đầu vào
│   ├── paragraph.txt              # Đoạn văn Privacy Policy (1,682 ký tự)
│   └── question.txt               # 8 câu hỏi truy vấn
│
├── wsd/                           # Word Sense Disambiguation
│   ├── data/
│   │   ├── reference_annotations.csv  # Ground truth (82 từ)
│   │   └── semcor_instances.jsonl     # Training data (73MB)
│   ├── models/
│   │   └── bert_semcor_model.pkl      # Trained BERT+SVM (48MB)
│   ├── results/
│   │   ├── mfs_eval.json              # MFS evaluation
│   │   ├── bert_eval.json             # BERT evaluation
│   │   ├── predictions_mfs.json       # MFS predictions
│   │   └── predictions_bert_semcor.json
│   ├── baseline_mfs.py            # MFS Baseline script
│   ├── prepare_semcor.py          # Chuẩn bị SemCor data
│   ├── train_bert.py              # Train BERT+SVM
│   └── predict_and_eval.py        # Evaluate BERT+SVM
│
├── kb/                            # Knowledge Base
│   ├── kb.pl                      # Prolog facts (26 facts)
│   ├── kb_aug.pl                  # WordNet augmentation (271 facts)
│   └── kb_fol.md                  # First-Order Logic representation
│
├── results/                       # Kết quả truy vấn
│   ├── queries.pl                 # Prolog queries
│   └── queries.md                 # Query documentation
│
├── augment/                       # WordNet Augmentation
│   └── wordnet_augment.py         # Script bổ sung synonym/hypernym
│
├── demo/                          # Web Demo (FastAPI)
│   ├── main.py                    # FastAPI backend
│   ├── templates/
│   │   └── index.html             # Main template
│   └── static/
│       ├── styles.css             # CSS styling
│       └── app.js                 # JavaScript logic
│
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

---

## ⚙️ Cài Đặt

### 1. Clone repository

```bash
git clone https://github.com/maibinhkznk209/CS229_Privacy_Semantic.git
cd CS229_Privacy_Semantic
```

### 2. Tạo virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# hoặc: .venv\Scripts\activate  # Windows
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 4. Download NLTK data

```bash
python -c "import nltk; nltk.download('wordnet'); nltk.download('semcor'); nltk.download('omw-1.4')"
```

---

## 🌐 Chạy Web Demo

### Khởi động server

```bash
python -m uvicorn demo.main:app --reload --port 8000
```

### Mở trình duyệt

Truy cập: **http://127.0.0.1:8000**

### Các tính năng:

| Tab | Mô tả |
|-----|-------|
| **Tổng Quan** | Thống kê dự án, đoạn văn Privacy Policy |
| **WSD** | Tra cứu từ, so sánh MFS vs BERT+SVM |
| **Tri Thức** | Knowledge Base (Prolog), FOL |
| **Truy Vấn** | Thực thi Prolog queries |
| **WordNet** | Synonyms, Hypernyms từ WordNet |

---

## 🏷️ WSD Models

### 1. MFS Baseline (Most Frequent Sense)

- **Phương pháp**: Zero-shot, sử dụng nghĩa đầu tiên từ WordNet
- **Không cần training**
- **Chạy**: `python wsd/baseline_mfs.py`

### 2. BERT + SVM

- **Phương pháp**: BERT embeddings + LinearSVC classifier
- **Training**: SemCor corpus (~200k instances)
- **Chạy train**: `python wsd/train_bert.py` (trên Kaggle với GPU)
- **Chạy eval**: `python wsd/predict_and_eval.py`

### 3. So sánh

| Model | Accuracy | Đúng/Tổng | Dataset |
|-------|----------|-----------|---------|
| **MFS Baseline** | 76.83% | 63/82 | reference_annotations.csv |
| **BERT + SVM** | ~67% | ~55/82 | reference_annotations.csv |

---

## 🧠 Knowledge Base

### Prolog Facts (`kb/kb.pl`)

```prolog
company(google).
collects(google, information).
uses_for(google, provide_services).
uses_technology(google, cookies).
...
```

### WordNet Augmentation (`kb/kb_aug.pl`)

```prolog
synonym(privacy, privateness).
synonym(privacy, seclusion).
is_a(privacy, reclusiveness).
...
```

### Truy vấn

```bash
swipl -q -f results/queries.pl
```

---

## 📊 Kết Quả

### WSD Evaluation

- **MFS Baseline**: 76.83% accuracy (63/82)
- **BERT + SVM**: ~67% accuracy (trained on SemCor)

### Knowledge Base

- **Original facts**: 26
- **Augmented facts**: 271 (202 synonyms + 69 hypernyms)

### Prolog Queries

8 câu truy vấn được thực thi thành công với kết quả chính xác.

---

## 📝 Ghi Chú

- Model BERT+SVM được train trên Kaggle (GPU T4)
- File `bert_semcor_model.pkl` có kích thước ~48MB
- File `semcor_instances.jsonl` có kích thước ~73MB

---

## 👥 Thành Viên

- (Thêm thông tin thành viên nhóm)

---

## 📚 Tham Khảo

- [NLTK WordNet](https://www.nltk.org/howto/wordnet.html)
- [SemCor Corpus](https://www.gabormelli.com/RKB/SemCor_Corpus)
- [HuggingFace Transformers](https://huggingface.co/transformers/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)