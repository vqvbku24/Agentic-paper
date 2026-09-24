# AGENT_SPEC.md — Disguise-and-Seek: Codebase cho Pilot (Giai đoạn 0–1)

> **Đối tượng đọc:** coding agent (Claude Code hoặc tương đương) và người phụ trách dự án.
> **Phiên bản:** v0.1 — 24/09/2026 (khớp với `Disguise_and_Seek_Research_Plan_v0.2.md`).
> **Phạm vi:** chỉ xây dựng hạ tầng và chạy **pilot không huấn luyện** (tuần 0–4 của kế hoạch). Kết quả pilot quyết định có đầu tư huấn luyện hay không.

---

## 0. Kickoff (dán đoạn này vào phiên làm việc đầu tiên)

```
Đọc toàn bộ AGENT_SPEC.md. Bắt đầu từ Milestone M0.
- Làm tuần tự theo milestone. Sau mỗi milestone: chạy test, ghi DECISIONS.md, tóm tắt ngắn cho tôi.
- Dừng và chờ tôi duyệt tại mọi điểm đánh dấu ⏸ (checkpoint). Không tự đi tiếp.
- Không bịa dữ liệu, không bịa số liệu, không tự diễn giải kết quả vượt quá những gì bảng số cho thấy.
- Nếu gặp điều kiện trong mục "Dừng và hỏi người" (Mục 12), dừng ngay và hỏi.
- Bắt đầu mọi bước tốn tiền (gọi LLM, embedding lớn) bằng lần chạy nhỏ (--limit 10), rồi mới chạy đầy đủ.
```

---

## 1. Mục tiêu và phạm vi

### 1.1 Cần xây dựng

Một codebase Python để trả lời ba câu hỏi pilot (Q1–Q3) và một phân tích headroom, **không huấn luyện mô hình**:

| Câu hỏi | Cần đo |
|---|---|
| **Q1.** Ý tưởng ngụy trang có đủ khó? | Recall của các baseline truy xuất cố định trên ý tưởng ngụy trang, theo phép ngụy trang và mức độ |
| **Q2.** "Mù văn liệu" có tồn tại? | Chênh lệch recall giữa tìm chỉ tiếng Anh và tìm đa ngữ, **theo điều kiện index** (có/không có abstract tiếng Anh của bài mục tiêu) |
| **Q3.** Agent có cần thiết? | Recall và chi phí của agent ReAct zero-shot so với pipeline cố định tốt nhất, ở ngân sách khớp; kèm headroom H1 (oracle định tuyến ngôn ngữ) |
| **H3.** Có rò rỉ tham số? | Recall của LLM khi *không có công cụ search* (closed-book) |

### 1.2 Sản phẩm đầu ra

1. Corpus đa ngôn ngữ đã chuẩn hóa và các index theo điều kiện.
2. Pipeline sinh ý tưởng ngụy trang (D1, D2, D3, D5) có kiểm tra hợp lệ.
3. Khung đánh giá tái lập được (metrics, bootstrap theo bài P).
4. Các baseline truy xuất cố định và một agent ReAct zero-shot.
5. `reports/pilot_report.md` tự sinh, có bảng số và kiểm tra ngưỡng quyết định.

### 1.3 Ngoài phạm vi (KHÔNG làm trong giai đoạn này)

- Không huấn luyện: SFT, RL, GRPO, self-play, conformal, fine-tune retriever.
- Không làm D4 (abstraction shift), ngôn ngữ thứ ba (ZH/JA), backbone lớn.
- Không dựng baseline deep-research agent hay OpenNovelty-style.
- Không thu thập dữ liệu vi phạm giấy phép (xem Mục 12).

Các phần này thuộc tầng Full/Stretch và sẽ có spec riêng nếu pilot vượt cổng G1.

---

## 2. Nguyên tắc làm việc (bắt buộc)

1. **Trung thực dữ liệu.** Không tạo dữ liệu giả để "cho chạy được". Mock chỉ dùng trong test và phải gắn nhãn rõ (`mock=True`, không bao giờ ghi vào `data/processed/` hay `runs/`).
2. **Tái lập.** Mọi lần chạy có `run_id`, lưu snapshot config, git commit hash, seed, phiên bản mô hình. Kết quả ghi ở `runs/<run_id>/`.
3. **Cache mọi lời gọi LLM và embedding** theo hash của (model, tham số, prompt). Cache phải bật mặc định.
4. **Kiểm soát chi phí.** Đọc `LLM_BUDGET_USD` từ biến môi trường; dừng cứng khi vượt. Ghi token và chi phí ước tính cho mỗi lời gọi.
5. **Bí mật.** API key chỉ lấy từ biến môi trường hoặc `.env` (đã `.gitignore`). Không commit key, dữ liệu thô, hay `runs/`.
6. **Không rò nhãn.** Agent và retriever *không bao giờ* thấy `source_doc_id`, `expected_preemption`, hay bất kỳ nhãn đánh giá nào (Mục 8.3). Có test tự động cho việc này.
7. **Bước nhỏ, kiểm chứng ngay.** Mỗi module có test; mỗi milestone có tiêu chí chấp nhận. Lỗi thì báo rõ, không nuốt (`fail loudly`).
8. **Ghi quyết định.** Mọi lựa chọn thiết kế không được spec quy định (thư viện thay thế, ngưỡng, xử lý ngoại lệ) ghi vào `DECISIONS.md` với lý do ngắn.
9. **Không diễn giải quá mức.** Báo cáo chỉ nêu số liệu và so sánh với ngưỡng đã cấu hình; nhãn "đạt/không đạt" là *heuristic* và phải ghi như vậy.

---

## 3. Môi trường và phụ thuộc

- **Python 3.11+**, quản lý bằng `uv` hoặc `pip` + `venv`; khóa phiên bản trong `pyproject.toml` + lockfile.
- Các thư viện gợi ý (agent có thể thay nếu có lý do, ghi vào `DECISIONS.md`):

| Mục đích | Gợi ý |
|---|---|
| Cấu hình, schema | `pydantic`, `pyyaml` |
| BM25 | `bm25s` (thuần Python); dự phòng `rank_bm25` |
| Embedding dense | `sentence-transformers` hoặc `FlagEmbedding` với `BAAI/bge-m3` |
| Chỉ mục vector | `faiss-cpu` (hoặc `faiss-gpu` nếu có GPU) |
| Tách từ | `underthesea` (tiếng Việt), `spacy` + `fr_core_news_sm` (tiếng Pháp) |
| Nhận diện ngôn ngữ | `lingua-language-detector` hoặc tương đương |
| PDF (nếu cần) | `pymupdf` |
| So khớp mờ tiêu đề | `rapidfuzz` |
| Dữ liệu | `pandas`, `pyarrow`, `datasets` (Hugging Face) |
| Thống kê | `numpy`, `scipy` |
| Retry/HTTP | `tenacity`, `httpx` |
| Test | `pytest` |
| CLI | `typer` hoặc `argparse` |

- **Tên package:** `dseek` (tránh `dns` vì trùng `dnspython`).
- **Phần cứng:** phải chạy được trên CPU cho các test và smoke run. Embedding BGE-M3 cho toàn corpus nên dùng GPU nếu có; nếu không, cấu hình `subsample` để giới hạn kích thước corpus khi pilot.
- **LLM:** truy cập qua lớp trừu tượng `LLMClient` (Mục 5). Tên mô hình và endpoint lấy từ `configs/models.yaml`, không hard-code.

---

## 4. Cấu trúc repo

```
disguise-and-seek/
├── AGENT_SPEC.md
├── DECISIONS.md              # agent ghi quyết định thiết kế
├── pyproject.toml
├── Makefile
├── .env.example
├── .gitignore                # data/, runs/, .env, cache/
├── configs/
│   ├── pilot.yaml            # cấu hình pilot chính
│   ├── index_conditions.yaml # định nghĩa điều kiện index
│   └── models.yaml           # tên mô hình, endpoint, giá
├── prompts/                  # mẫu prompt (Phụ lục A)
│   ├── facets.md  d1_drift.md  d2_subset.md  d3_roundtrip.md
│   ├── d5_scrub_check.md  judge_preemption.md  hunter_system.md
├── src/dseek/
│   ├── schemas.py            # pydantic: Document, Idea, RunRecord, Hit...
│   ├── config.py
│   ├── cli.py
│   ├── llm/        client.py cache.py budget.py mock.py
│   ├── data/       adapters/{acl_anthology.py, vi_journals.py, checkthat.py}  build_corpus.py
│   ├── index/      views.py bm25.py dense.py hybrid.py
│   ├── retrieval/  base.py translate.py brute_force.py oracle.py closed_book.py
│   ├── disguise/   facets.py operators.py scrub.py validate.py pipeline.py
│   ├── agent/      tools.py react.py budget.py parsing.py
│   ├── eval/       metrics.py bootstrap.py runner.py report.py
│   └── annotate/   export.py import_.py kappa.py
├── scripts/
├── tests/
├── data/                     # gitignored: raw/  processed/  index/
├── runs/                     # gitignored
└── reports/
```

---

## 5. Lớp LLM (`dseek/llm`)

**Yêu cầu:**

- Giao diện chung: `LLMClient.complete(messages, model, temperature, max_tokens, tools=None, seed=None) -> LLMResponse`.
- Hỗ trợ ít nhất: (a) một provider đóng qua API; (b) endpoint tương thích OpenAI (cho mô hình mở phục vụ bằng vLLM/khác). Provider cụ thể do người dùng chọn (Mục 12).
- **Cache** trên đĩa (SQLite hoặc thư mục hash) khóa theo (provider, model, messages, tham số). Có cờ `--no-cache` để bỏ qua.
- **Budget guard:** cộng dồn chi phí ước tính (bảng giá trong `configs/models.yaml`); ném `BudgetExceeded` khi vượt `LLM_BUDGET_USD`.
- **Retry** có backoff với lỗi tạm thời; không retry lỗi nội dung (4xx không phải rate limit).
- **`MockLLM`** trả lời xác định để test pipeline; luôn gắn `mock=True` trong metadata.
- **Tool calling:** ưu tiên tool-calling gốc của provider; nếu mô hình không hỗ trợ, dùng định dạng JSON-action với validate schema (Mục 9.3).

**Tiêu chí chấp nhận:** test cache (gọi hai lần, lần hai không tốn chi phí), test budget (vượt ngân sách thì dừng), test mock.

---

## 6. Schema dữ liệu (`dseek/schemas.py`)

Dùng JSONL cho mọi tập dữ liệu; validate bằng pydantic khi đọc/ghi.

### 6.1 Document

```json
{
  "doc_id": "2024.jeptalnrecital-long.7",
  "source": "acl_anthology",
  "lang": "fr",
  "title_native": "…",
  "abstract_native": "…",
  "title_en": "…",
  "abstract_en": "…",
  "has_en_abstract": true,
  "year": 2024,
  "venue": "jeptalnrecital",
  "url": "https://…",
  "license": "CC-BY-4.0",
  "body_path": null
}
```

- `doc_id` ổn định, duy nhất. Với ACL Anthology dùng ID của Anthology.
- `lang` ∈ {`en`, `fr`, `vi`}, do metadata + kiểm tra nhận diện ngôn ngữ (ghi cảnh báo khi không khớp).
- Chuẩn hóa Unicode NFC cho mọi văn bản (quan trọng cho tiếng Việt).
- `abstract_en = null` khi tài liệu không có abstract tiếng Anh do tác giả viết. **Không** tự sinh abstract EN bằng dịch máy vào trường này; bản dịch máy đi vào trường riêng `abstract_en_mt` (dùng cho baseline translate-doc, nếu bật).

### 6.2 Idea (ý tưởng ngụy trang)

```json
{
  "idea_id": "idea_000123",
  "source_doc_id": "2024.jeptalnrecital-long.7",
  "generator": "llm",
  "operators": [
    {"name": "D1", "level": 2},
    {"name": "D2", "mode": "drop_secondary"},
    {"name": "D3", "level": 1, "pivot_langs": ["vi"]},
    {"name": "D5", "applied": true}
  ],
  "text_en": "…",
  "facets": {"purpose": "…", "mechanism": "…", "evaluation": "…"},
  "preemption_label": "full",
  "validity": {
    "judge_model": "…",
    "label": "full",
    "confidence": 0.86,
    "second_judge_label": "full",
    "agree": true,
    "human_label": null
  },
  "shortcut": {"bm25_top1_hit": false, "ngram3_jaccard": 0.04},
  "split": "pilot",
  "seed": 1234
}
```

### 6.3 Hit và RunRecord

```json
// Hit
{"doc_id": "…", "score": 12.3, "view": "native", "lang": "fr", "rank": 1}

// RunRecord (một dòng mỗi tác vụ và mỗi hệ)
{
  "run_id": "…", "system": "hybrid_fixed", "condition": "en_only_blind",
  "budget": 10, "idea_id": "…",
  "ranked_doc_ids": ["…"],          // đã khử trùng theo doc_id
  "cost": {"n_search": 3, "tokens_in": 0, "tokens_out": 0, "usd": 0.0},
  "trajectory_path": null,          // đường dẫn tới log agent (nếu là agent)
  "verdict": null, "confidence": null
}
```

---

## 7. Corpus và điều kiện index

### 7.1 Nguồn dữ liệu (pilot)

| Vai trò | Nguồn | Ghi chú |
|---|---|---|
| Bài mục tiêu P (FR) và kho FR | JEP/TALN/RECITAL trong ACL Anthology | Lấy metadata + abstract (có thể có abstract EN); kiểm tra giấy phép theo metadata |
| Kho phân tán EN (distractor) | Bài tiếng Anh trong ACL Anthology (cs.CL) | Kích thước cấu hình được (`en_pool_size`) |
| Bài mục tiêu P (VI) và kho VI | Tạp chí Việt Nam (VJST, VNU JCS, VAST JCC, …) | **Chưa chốt nguồn.** Adapter là plugin; xem Mục 12 |
| Sanity E5 | CheckThat! 2026 Task 1 | Hugging Face: `sschellhammer/CT26_Task1_SourceRetrievalForScientificWebClaims` |

**Việc phải làm ở M1:** viết `docs/DATA_SOURCES.md` ghi từng nguồn: cách truy cập, giấy phép quan sát được, số lượng bài, tỉ lệ có abstract EN, năm xuất bản. Nếu không xác định được giấy phép, **dừng và hỏi người** (Mục 12).

### 7.2 Ba "view" và bốn điều kiện index

Mỗi tài liệu được lập chỉ mục dưới nhiều *view*. Mọi kết quả truy xuất được khử trùng về `doc_id`.

| View | Nội dung | Ngôn ngữ chỉ mục |
|---|---|---|
| `V_en_corpus` | Văn bản gốc của các bài tiếng Anh (title + abstract) | en |
| `V_en_abs` | `abstract_en` + `title_en` của bài FR/VI (nếu có) | en |
| `V_native` | `abstract_native` + `title_native` của bài FR/VI | fr / vi |

Điều kiện index (định nghĩa trong `configs/index_conditions.yaml`):

| Điều kiện | View tìm được | Ý nghĩa |
|---|---|---|
| `en_only_blind` | `V_en_corpus` | Hệ thống thuần tiếng Anh; bài FR/VI *vô hình* (index blindness) |
| `en_only_with_abs` | `V_en_corpus` + `V_en_abs` | Hệ thống tiếng Anh nhưng có abstract EN của bài FR/VI |
| `native_only` | `V_native` | Chỉ văn bản bản địa |
| `all` | cả ba view | Đầy đủ |

**Ràng buộc:** trong `en_only_blind`, không tài liệu FR/VI nào được phép xuất hiện trong kết quả. Viết test khẳng định điều này.

### 7.3 Chỉ mục

- **BM25:** một chỉ mục riêng cho mỗi (view, ngôn ngữ). Tokenization: `underthesea` cho VI; spaCy (bỏ dấu câu, lowercase, lemma tùy chọn) cho FR; tách đơn giản + stopword cho EN. Ghi lựa chọn vào `DECISIONS.md`.
- **Dense:** BGE-M3 (`BAAI/bge-m3`), chuẩn hóa vector, FAISS (inner product). Lưu embedding ra đĩa để dùng lại.
- **Hybrid:** kết hợp BM25 và dense bằng Reciprocal Rank Fusion (tham số `k=60`, cấu hình được).

**Tiêu chí chấp nhận:** với mọi điều kiện, `search()` trả về kết quả xác định (deterministic) khi cùng seed; test rò rỉ view; test tokenization VI/FR trên ví dụ có dấu.

---

## 8. Pipeline sinh ý tưởng ngụy trang

### 8.1 Các bước

```
Document P
   └─ facets.py      : trích lát cắt (purpose, mechanism, evaluation) + danh sách thuật ngữ kỹ thuật chính + định danh cần loại bỏ
   └─ operators.py   : áp D2 → D1 → D3 (thứ tự cố định)
   └─ scrub.py       : D5 (luôn bật)
   └─ validate.py    : judge xác nhận mức pre-emption; đo shortcut
   └─ pipeline.py    : điều phối, ghi Idea JSONL
```

### 8.2 Đặc tả các phép ngụy trang

| Mã | Yêu cầu | Tham số |
|---|---|---|
| **D1 terminology drift** | Thay thuật ngữ kỹ thuật chính bằng khái niệm tương đương, mô tả vòng, hoặc cách gọi của cộng đồng khác. **Không thêm tuyên bố mới, không đổi ý nghĩa.** Mức 0: giữ nguyên; 1: thay khoảng một nửa thuật ngữ chính; 2: thay tất cả thuật ngữ chính; 3: như 2 và viết lại bằng từ vựng của một cộng đồng khác | `level ∈ {0,1,2,3}` |
| **D2 facet subsetting** | `drop_secondary`: bỏ lát cắt đánh giá (kỳ vọng vẫn `full`). `graft_twist`: giữ mục đích và một phần cơ chế của P, thêm một biến thể/khía cạnh **không có trong P** (kỳ vọng `partial`) | `mode ∈ {none, drop_secondary, graft_twist}` |
| **D3 cross-lingual round-trip** | Dịch ý tưởng (EN) sang ngôn ngữ trung gian rồi về EN; mức 2 dùng hai ngôn ngữ trung gian. Dùng LLM hoặc MT; cố định một hệ cho toàn bộ pilot | `level ∈ {0,1,2}`, `pivot_langs` |
| **D5 anti-shortcut scrub** | Loại tên riêng, tên dataset/acronym đặc thù, số liệu cụ thể xuất hiện trong P. Kiểm bằng regex và một lượt LLM; xác nhận không còn định danh | luôn bật |

### 8.3 Kiểm tra hợp lệ và đường tắt

**Judge pre-emption** (`prompts/judge_preemption.md`): nhận (I, P) và trả về JSON `{label: full|partial|none, confidence, rationale}`.

- Với pilot, P được biểu diễn bằng `title + abstract_native + abstract_en (nếu có)`. Ghi rõ giới hạn "chưa dùng toàn văn" trong báo cáo.
- Chạy với **hai judge khác họ mô hình** nếu có thể; lưu `agree`.
- **Giữ** mẫu khi nhãn judge ∈ {`full`, `partial`}; **loại** mẫu `none`. `preemption_label` lấy từ judge (không lấy từ ý định ban đầu của operator).
- Báo cáo: tỉ lệ giữ, tỉ lệ đồng thuận hai judge, phân bố nhãn theo operator/level.

**Đo đường tắt:**

- `bm25_top1_hit`: chạy BM25 (điều kiện `all`) với `text_en` nguyên văn; đánh dấu nếu P ở top-1.
- `ngram3_jaccard`: độ trùng 3-gram từ giữa `text_en` và văn bản của P.
- Không loại mẫu shortcut-prone; dùng để phân tầng kết quả.

**Không rò nhãn:** kiểm tra tự động rằng `text_en` không chứa tiêu đề của P và không chứa `doc_id`.

### 8.4 Quy mô pilot và lấy mẫu

- `n_source`: 200–500 bài P (cấu hình; báo cáo số bài có sẵn theo ngôn ngữ và năm).
- `variants_per_source`: 3–6 biến thể, chọn tổ hợp (D1 level × D2 mode × D3 level) bằng **lấy mẫu phân tầng có seed**, đảm bảo mỗi ô chính có ít nhất vài chục mẫu trên tổng thể.
- Ưu tiên bài P xuất bản gần đây để giảm rủi ro rò rỉ tham số; ghi `year` và phân tầng kết quả theo năm.

**Vòng kiểm định chất lượng bắt buộc (⏸ sau M3):** sinh 20 mẫu → in ra để người duyệt (I, tóm tắt P, nhãn judge) → điều chỉnh prompt → lặp lại. Không sinh hàng loạt trước khi người duyệt.

---

## 9. Baseline truy xuất và agent

### 9.1 Giao diện chung

```python
class Retriever(Protocol):
    def search(self, query: str, k: int, condition: str) -> list[Hit]: ...
```

Mọi hệ nhận **ý tưởng `text_en` và điều kiện index**, không nhận thứ gì khác về tác vụ.

### 9.2 Danh sách baseline (pilot)

| ID | Hệ | Mô tả |
|---|---|---|
| B0a | `bm25_en` | BM25, truy vấn EN nguyên văn |
| B0b | `dense_bge_m3` | Dense BGE-M3 |
| B0e | `hybrid_fixed` | BM25 + dense (RRF) |
| B0c | `translate_query` | Dịch truy vấn sang {fr, vi} rồi BM25/dense theo ngôn ngữ, hợp nhất bằng RRF |
| B0d | `brute_force_multilingual` | Luôn tìm ở mọi ngôn ngữ/view, hợp nhất (cận trên chi phí) |
| U1 | `oracle_routing` | Biết ngôn ngữ của P; dịch truy vấn sang đúng ngôn ngữ đó và chỉ tìm ở view tương ứng. *Chỉ để chẩn đoán headroom; ghi rõ là oracle, không phải hệ khả thi* |
| H3 | `closed_book` | LLM không có công cụ, liệt kê tối đa 10 tiêu đề bài có thể hóa giải ý tưởng; khớp mờ với tiêu đề trong corpus (`rapidfuzz`, ngưỡng cấu hình mặc định 90) → danh sách `doc_id` |
| B3a | `react_zero_shot` | Agent ReAct zero-shot (Mục 9.3) |

**Ghi chú:** B-CT (pipeline kiểu Claim2Source), B1a/b (Idea Novelty Checker) và translate-doc thuộc bước mở rộng sau pilot; không làm trong M0–M7 trừ khi người yêu cầu.

### 9.3 Agent ReAct zero-shot

**Công cụ:**

| Tool | Tham số | Trả về |
|---|---|---|
| `search` | `query: str`, `lang: en|fr|vi`, `backend: bm25|dense|hybrid`, `view: en_corpus|en_abs|native|all` | Top-n snippet (`doc_id`, `title`, đoạn đầu abstract, `lang`, `view`) |
| `translate` | `text: str`, `target_lang` | Văn bản đã dịch |
| `read` | `doc_id: str` | Title + abstract (native và EN nếu có) |
| `note` | `text: str` | Lưu ghi chú vào bộ nhớ làm việc |
| `answer` | `top_k: list[doc_id]`, `verdict`, `confidence` | Kết thúc episode |

**Ràng buộc:**

- Điều kiện index được áp bởi *hạ tầng*: nếu `condition = en_only_blind` thì tool `search` với `view=native` bị từ chối (trả lỗi rõ ràng) hoặc không trả gì từ view bị cấm. Agent không tự thay đổi điều kiện.
- **Ngân sách:** giới hạn số lần `search` (mức 5/10/20), số lượt tối đa (`max_turns=12`) và token; vượt thì buộc `answer`.
- Chỉ được trích `doc_id` đã xuất hiện trong kết quả (harness kiểm tra; `doc_id` lạ bị loại và ghi nhận `hallucinated_id`).
- `hunter_system.md` mô tả vai trò, công cụ, ngân sách, định dạng đầu ra; nhấn mạnh ý tưởng có thể dùng thuật ngữ khác hoặc đã qua dịch, và tài liệu tiền nghiệm có thể viết bằng ngôn ngữ khác.
- **Search certificate** được harness dựng tự động từ log (danh sách truy vấn, ngôn ngữ, view, lý do dừng), không do LLM tự khai.
- Log toàn bộ quỹ đạo vào `runs/<run_id>/trajectories/<idea_id>.jsonl`.

**Tiêu chí chấp nhận:** chạy được với `MockLLM` end-to-end; test ngân sách (không vượt); test từ chối view bị cấm; test loại `doc_id` bịa.

---

## 10. Khung đánh giá (`dseek/eval`)

### 10.1 Chỉ số

- **Recall@k** (k = 1, 5, 10): `P ∈ top-k` (pilot chỉ dùng P và các bản trùng cùng `doc_id`).
- **MRR** và hạng của P.
- **Chi phí:** số `search`, token, USD.
- Với agent: tỉ lệ `hallucinated_id`, số lượt trung bình, phân bố ngôn ngữ đã tìm.

### 10.2 Thống kê

- **Bootstrap tái lấy mẫu theo `source_doc_id`** (cụm), 1.000–10.000 lần, khoảng tin cậy 95%. Các ý tưởng từ cùng P tương quan; **không** bootstrap theo `idea_id`.
- So sánh hai hệ: hiệu số ghép cặp trên cùng tác vụ, bootstrap theo cụm.
- Đọc kết quả ở **3 mức ngân sách** cho mọi hệ có khái niệm ngân sách; hệ cố định dùng số truy vấn tương ứng.

### 10.3 Chia tầng báo cáo

Mỗi bảng chính phải có các lát cắt: theo ngôn ngữ của P (fr/vi), theo điều kiện index, theo mức D1, theo mức D3, theo D2 mode, theo `shortcut-prone` hay không, theo năm xuất bản.

### 10.4 Kiểm tra sanity E5 (CheckThat! 2026 Task 1)

- Tải tập dev (hoặc tập con) từ Hugging Face; chạy BM25 và dense BGE-M3 trên kho 10.000 bài; tính **MRR@5**.
- Chỉ báo cáo số đo và so sánh với mức đã công bố của các hệ tham gia (chỉ để phát hiện lỗi cài đặt rõ rệt, ví dụ MRR gần 0). Không kỳ vọng khớp hệ đứng đầu.

### 10.5 Kiểm tra tiền nghiệm hợp lệ khác (audit nhỏ, tùy chọn)

Lấy mẫu ~50 tác vụ mà P không ở top-10; với top-3 doc không phải P, nhờ judge xác nhận có hóa giải ý tưởng không. Ước lượng tỉ lệ "miss thật" bị đánh giá thấp do chỉ tính P. Chỉ báo cáo số đo.

---

## 11. Báo cáo pilot (`reports/pilot_report.md`, tự sinh)

Cấu trúc bắt buộc:

1. **Dữ liệu:** số bài theo ngôn ngữ/năm, tỉ lệ có abstract EN, kích thước corpus, nguồn và giấy phép.
2. **Chất lượng ngụy trang:** tỉ lệ giữ, đồng thuận judge, phân bố nhãn, shortcut-rate, κ (nếu đã có nhãn người), 10 ví dụ ngẫu nhiên.
3. **Kết quả baseline:** bảng Recall@{1,5,10}, MRR, chi phí theo hệ × điều kiện index × ngân sách, kèm khoảng tin cậy.
4. **Lát cắt:** theo ngôn ngữ, phép ngụy trang, mức, shortcut.
5. **Q1–Q3 và H1, H3:** đối chiếu với ngưỡng trong `configs/pilot.yaml` (mặc định gợi ý bên dưới) và ghi rõ đây là ngưỡng heuristic.
6. **Sanity E5.**
7. **Vấn đề đã biết và hạn chế** (ví dụ: chưa dùng toàn văn, judge giới hạn, kho VI nhỏ).

Ngưỡng mặc định trong config (có thể chỉnh):

```yaml
thresholds:
  q1_hard_enough_recall_at_10_max: 0.85     # ≤ 0.85: đủ khó; 0.85–0.90: cần tăng mức; ≥ 0.90: chưa đủ khó
  q2_gap_min_points: 10                     # chênh EN-only vs đa ngữ (điều kiện abstract EN vắng)
  q3_agent_gain_min_points: 5               # agent hơn pipeline cố định tốt nhất
  q3_cost_ratio_max_at_parity: 0.5          # hoặc ngang (≤2 điểm) với chi phí ≤ 50%
  parity_tolerance_points: 2
  h1_headroom_min_points: 5                 # oracle định tuyến so với cố định tốt nhất
```

Báo cáo chỉ đưa ra bảng "đạt/không đạt theo ngưỡng"; **quyết định go/no-go do con người đưa ra.**

---

## 12. Dừng và hỏi người

Dừng lại, tóm tắt vấn đề và đề xuất lựa chọn, khi gặp bất kỳ điều nào sau:

1. **Giấy phép không rõ** hoặc điều khoản cấm thu thập/tái phân phối dữ liệu (đặc biệt tạp chí Việt Nam, Érudit/CLIRudit).
2. **Nguồn VI chưa chốt** hoặc không tải được hợp lệ. Khi đó, hoàn thành pilot cho FR trước và giữ adapter VI dạng plugin.
3. **Chọn provider/mô hình LLM và ngân sách** (`LLM_BUDGET_USD`) chưa được người cấp.
4. Tỉ lệ giữ mẫu sau kiểm tra hợp lệ **dưới 40%**, hoặc đồng thuận hai judge thấp bất thường: dừng và trình mẫu để người xem lại prompt.
5. Số bài P có sẵn (sau lọc) **dưới 150** cho một ngôn ngữ.
6. Kết quả vô lý (ví dụ Recall@10 của mọi hệ đều ≈ 0 hoặc ≈ 1): nghi lỗi hạ tầng hoặc rò nhãn; báo cáo chẩn đoán trước khi tiếp tục.
7. Chi phí ước tính của lần chạy đầy đủ vượt 50% ngân sách còn lại.
8. Cần dùng dữ liệu có thể chứa thông tin cá nhân.

---

## 13. Milestone và tiêu chí chấp nhận

Ánh xạ thời gian: M0–M1 ≈ tuần 0–1; M2–M4 ≈ tuần 1–2; M5–M6 ≈ tuần 3; M7 ≈ tuần 4.

### M0 — Khung dự án (⏸ không cần duyệt, chỉ báo cáo)

- Tạo cấu trúc repo, `pyproject.toml`, `Makefile` (`make test`, `make lint`), `.gitignore`, `.env.example`.
- `schemas.py`, `config.py`, `cli.py` khung, `llm/` (client, cache, budget, mock).
- **Chấp nhận:** `make test` xanh; test cache, budget, mock, schema round-trip.

### M1 — Dữ liệu và corpus (⏸ checkpoint dữ liệu)

- Adapter ACL Anthology (FR + EN pool); adapter CheckThat!; khung adapter VI (plugin).
- `build_corpus`: chuẩn hóa NFC, nhận diện ngôn ngữ, khử trùng, ghi `data/processed/docs.jsonl`.
- Viết `docs/DATA_SOURCES.md` (Mục 7.1) và thống kê corpus.
- **Chấp nhận:** schema hợp lệ 100%; báo cáo số lượng theo ngôn ngữ/năm/có abstract EN; kiểm tra giấy phép ghi trong tài liệu.
- **⏸ Người duyệt:** nguồn VI, giấy phép, tỉ lệ có abstract EN (quyết định G0).

### M2 — Index và truy xuất cố định

- `views.py`, `bm25.py`, `dense.py`, `hybrid.py`; điều kiện index (Mục 7.2).
- Baseline B0a, B0b, B0e chạy được qua CLI.
- **Chấp nhận:** test rò rỉ view (`en_only_blind` không trả bài FR/VI); test tokenization; smoke run trên 20 truy vấn giả lập từ tiêu đề bài (Recall@10 hợp lý, không bằng 0 hay 1 toàn bộ).

### M3 — Pipeline ngụy trang (⏸ duyệt 20 mẫu)

- `facets.py`, `operators.py`, `scrub.py`, `validate.py`, `pipeline.py`; prompt ở Phụ lục A.
- Sinh 20 mẫu → người duyệt → chỉnh prompt.
- **Chấp nhận:** mỗi mẫu có đủ trường Idea; không rò tiêu đề/ID; judge chạy được; báo cáo tỉ lệ giữ và đồng thuận.

### M4 — Sinh pilot và xuất nhãn người

- Sinh 500–1.500 ý tưởng theo Mục 8.4 (sau khi người duyệt M3).
- `annotate.export`: xuất CSV cho annotator (cột: `idea_id`, `text_en`, tóm tắt P, nhãn judge ẩn hoặc hiện theo cấu hình; cột nhãn người). `annotate.import_` và `kappa.py` (Cohen's κ).
- **Chấp nhận:** xuất/nhập khứ hồi giữ nguyên dữ liệu; test κ trên ví dụ nhỏ có đáp án tay.

### M5 — Khung đánh giá và các baseline còn lại

- `eval/` (metrics, bootstrap theo cụm, runner, report khung).
- B0c, B0d, U1, H3 (closed-book).
- **Chấp nhận:** test metric với ví dụ tay; test bootstrap theo cụm (kết quả thay đổi hợp lý khi gộp/tách cụm); chạy toàn bộ baseline cố định trên tập pilot.

### M6 — Agent ReAct zero-shot (⏸ trước khi chạy đầy đủ)

- `agent/` theo Mục 9.3; chạy thử `--limit 10` với `MockLLM` rồi với LLM thật.
- **⏸ Người duyệt:** chi phí ước tính cho lần chạy đầy đủ ở 3 ngân sách, và mẫu quỹ đạo.
- **Chấp nhận:** test ngân sách/từ chối view/loại `doc_id` bịa; quỹ đạo được log đủ.

### M7 — Pilot đầy đủ và báo cáo (⏸ duyệt kết quả)

- Chạy đầy đủ mọi hệ ở 3 ngân sách và 4 điều kiện index; E5; audit tùy chọn.
- Sinh `reports/pilot_report.md`.
- **Chấp nhận:** báo cáo đầy đủ mục 1–7; mọi bảng có khoảng tin cậy theo cụm; có thể tái lập từ `run_id`.
- **⏸ Người duyệt:** đọc báo cáo và quyết định G1 (huấn luyện hay đổi hướng). Agent *không* tự kết luận hướng đi.

---

## 14. Test bắt buộc (tối thiểu)

| Nhóm | Nội dung |
|---|---|
| Schema | Round-trip Document/Idea/RunRecord; trường bắt buộc |
| LLM | Cache hit; budget dừng đúng; mock xác định |
| Index | Không rò view theo điều kiện; khử trùng theo `doc_id`; xác định theo seed |
| Tokenization | Ví dụ VI/FR có dấu, NFC |
| Disguise | D5 loại định danh (regex); không chứa tiêu đề/ID của P; xử lý JSON hỏng từ LLM |
| Chống rò nhãn | Hàm truy xuất/agent không nhận `source_doc_id`, `preemption_label`; kiểm tra bằng inspection của chữ ký hàm và test tích hợp |
| Metric | Recall@k, MRR, bootstrap theo cụm bằng ví dụ tay |
| Agent | Ngân sách; từ chối view bị cấm; loại `doc_id` bịa; parse hành động sai định dạng |
| Sanity | Smoke test E5 trên tập rất nhỏ |

---

## 15. Cấu hình mẫu (`configs/pilot.yaml`)

```yaml
run:
  seed: 1234
  cache_dir: data/cache
  budget_usd_env: LLM_BUDGET_USD

corpus:
  languages: [fr, vi, en]
  en_pool_size: 20000
  min_year_for_targets: 2020        # ưu tiên bài gần đây làm P
  subsample: null                   # đặt số nếu chạy CPU

disguise:
  n_source: 300
  variants_per_source: 4
  d1_levels: [0, 1, 2, 3]
  d2_modes: [none, drop_secondary, graft_twist]
  d3_levels: [0, 1, 2]
  pivot_langs: [vi, fr]
  judge_models: [judge_a, judge_b]  # khác họ mô hình nếu có thể
  keep_labels: [full, partial]

retrieval:
  top_k: 10
  rrf_k: 60
  dense_model: BAAI/bge-m3

agent:
  model: hunter_model               # tham chiếu configs/models.yaml
  max_turns: 12
  search_budgets: [5, 10, 20]
  snippet_chars: 400

closed_book:
  n_titles: 10
  fuzzy_threshold: 90

eval:
  ks: [1, 5, 10]
  bootstrap_iters: 5000
  cluster_by: source_doc_id

conditions: [en_only_blind, en_only_with_abs, native_only, all]
```

---

## 16. Lệnh CLI kỳ vọng

```bash
dseek data build --config configs/pilot.yaml
dseek index build --conditions all
dseek disguise generate --config configs/pilot.yaml --limit 20      # bước duyệt M3
dseek disguise generate --config configs/pilot.yaml                 # sinh đầy đủ (sau khi duyệt)
dseek disguise validate --config configs/pilot.yaml
dseek annotate export --n 100 --out data/annotation/batch1.csv
dseek annotate import --in data/annotation/batch1_done.csv
dseek eval baseline --name hybrid_fixed --condition en_only_blind --budget 10
dseek eval baseline --name closed_book
dseek agent run --config configs/pilot.yaml --budgets 5,10,20 --limit 10
dseek eval sanity-checkthat --split dev --limit 500
dseek report pilot --run-id <run_id>
```

---

## Phụ lục A — Khung prompt (điểm khởi đầu; agent tinh chỉnh qua vòng duyệt M3)

Mỗi prompt lưu trong `prompts/*.md`, có biến `{{...}}`, yêu cầu **đầu ra JSON hợp lệ** và được validate bằng pydantic; nếu JSON hỏng thì thử lại tối đa 2 lần rồi ghi lỗi.

### A.1 `facets.md`

```
Bạn là trợ lý phân tích bài báo NLP. Cho tiêu đề và abstract sau (có thể bằng tiếng Pháp/Việt và bản tiếng Anh):
{{title}} / {{abstract_native}} / {{abstract_en}}

Trả về JSON:
{
  "purpose": "mục đích/bài toán (1–2 câu, tiếng Anh)",
  "mechanism": "cơ chế/kỹ thuật cốt lõi (1–3 câu, tiếng Anh)",
  "evaluation": "thiết lập đánh giá (1 câu, tiếng Anh)",
  "key_terms": ["thuật ngữ kỹ thuật chính (tiếng Anh)", ...],
  "identifiers": ["tên riêng, tên dataset, acronym đặc thù, con số cụ thể", ...]
}
Chỉ dùng thông tin có trong văn bản. Không thêm suy đoán.
```

### A.2 `d1_drift.md`

```
Viết lại mô tả ý tưởng nghiên cứu sau bằng tiếng Anh, giữ nguyên ý nghĩa khoa học nhưng thay thuật ngữ:
Ý tưởng: {{idea_text}}
Thuật ngữ chính: {{key_terms}}
Mức drift: {{level}}  (1: thay khoảng một nửa thuật ngữ chính; 2: thay tất cả; 3: như 2 và dùng từ vựng của một cộng đồng nghiên cứu khác)
Quy tắc:
- Dùng từ đồng nghĩa, cách gọi khác, hoặc mô tả vòng (mô tả bằng lời thay cho tên kỹ thuật).
- KHÔNG thêm tuyên bố, kết quả hay chi tiết mới. KHÔNG bỏ đóng góp cốt lõi.
Trả về JSON: {"idea_text": "..."}
```

### A.3 `d2_subset.md`

```
Chế độ: {{mode}}
- drop_secondary: bỏ phần thiết lập đánh giá, giữ mục đích và cơ chế.
- graft_twist: giữ mục đích và một phần cơ chế của ý tưởng gốc, rồi THÊM một biến thể/khía cạnh mới KHÔNG có trong bài gốc (nêu trong "added_twist").
Ý tưởng gốc (lát cắt): {{facets}}
Trả về JSON: {"idea_text": "...", "added_twist": null | "..."}
```

### A.4 `d3_roundtrip.md`

Dùng LLM hoặc MT: dịch `idea_text` sang `{{pivot_lang}}` rồi dịch ngược sang tiếng Anh, mỗi bước là một lời gọi độc lập (không cho mô hình thấy văn bản gốc ở bước dịch ngược). Ghi cả bản trung gian vào log.

### A.5 `d5_scrub_check.md`

```
Cho ý tưởng: {{idea_text}} và danh sách định danh cần loại: {{identifiers}}
1) Liệt kê định danh nào còn xuất hiện (kể cả biến thể viết khác).
2) Viết lại để loại chúng, giữ nguyên ý nghĩa.
Trả về JSON: {"remaining": [...], "idea_text": "..."}
```

### A.6 `judge_preemption.md` (quan trọng nhất)

```
Bạn là chuyên gia thẩm định tính mới. Cho:
- Ý tưởng nghiên cứu mới (I): {{idea_text}}
- Bài báo đã công bố (P): tiêu đề {{title}}, abstract {{abstract_native}} / {{abstract_en}}

Xác định mức bài P hóa giải ý tưởng I:
- "full": P đã bao hàm, hoặc làm hiển nhiên đối với chuyên gia, mọi lát cắt cốt lõi của I (mục đích và cơ chế).
- "partial": P hóa giải ít nhất một lát cắt cốt lõi của I nhưng không đủ toàn bộ.
- "none": P không hóa giải lát cắt cốt lõi nào của I.
Chỉ dựa vào nội dung được cung cấp; không suy diễn ngoài văn bản.
Trả về JSON: {"label": "full|partial|none", "confidence": 0.0-1.0, "rationale": "tối đa 3 câu"}
```

### A.7 `hunter_system.md`

```
Bạn là agent tìm tiền nghiệm. Nhiệm vụ: cho một ý tưởng nghiên cứu (tiếng Anh), tìm các bài đã công bố hóa giải ý tưởng đó.
Lưu ý: ý tưởng có thể dùng thuật ngữ khác với bài gốc hoặc đã qua dịch; bài tiền nghiệm có thể viết bằng ngôn ngữ khác (ví dụ tiếng Pháp, tiếng Việt).
Công cụ: search, translate, read, note, answer. Ngân sách: tối đa {{n_search}} lần search và {{max_turns}} lượt.
Quy tắc:
- Chỉ trích doc_id đã xuất hiện trong kết quả công cụ. Không bịa doc_id.
- Cân nhắc tìm bằng nhiều ngôn ngữ khi tìm bằng tiếng Anh cho kết quả yếu.
- Khi kết thúc, gọi answer với top_k (tối đa 10 doc_id, xếp theo độ hóa giải giảm dần), verdict (pre_empted | partially_pre_empted | none_found) và confidence.
```

---

## Phụ lục B — Những sai lầm cần tránh

| Sai lầm | Hậu quả | Cách tránh |
|---|---|---|
| Để abstract EN của P lọt vào điều kiện `en_only_blind` | Đo sai "mù văn liệu" | Test rò view; index theo view riêng |
| Bootstrap theo `idea_id` | Khoảng tin cậy quá hẹp | Bootstrap theo `source_doc_id` |
| Đưa nhãn vào agent/retriever | Kết quả vô nghĩa | Chữ ký hàm không nhận nhãn; test chống rò |
| Dùng cùng mô hình làm proposer và judge | Thiên vị tự ưa | Judge khác họ mô hình; báo cáo đồng thuận |
| Sinh hàng loạt trước khi duyệt mẫu | Tốn chi phí, dữ liệu kém | Checkpoint M3 |
| Không cache LLM | Chi phí vọt, không tái lập | Cache mặc định |
| Diễn giải "đạt ngưỡng" thành kết luận khoa học | Kết luận sớm | Báo cáo chỉ nêu số và ngưỡng heuristic |
| Trộn bản dịch máy vào `abstract_en` | Làm sạch nhãn "abstract của tác giả" | Trường `abstract_en_mt` riêng |
| Quên chuẩn hóa NFC cho tiếng Việt | Lỗi khớp BM25 | Chuẩn hóa ở `build_corpus` |
