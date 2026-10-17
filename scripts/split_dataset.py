# -*- coding: utf-8 -*-
"""
Script: split_dataset.py
Mục đích: Tách bộ dữ liệu 683 câu hỏi luật giao thông thành 3 tập Train (80%), Val (10%), Test (10%)
theo phương pháp phân tầng đều (Stratified Sampling theo từng khối chủ đề).
Xuất ra định dạng:
- data/processed/train.jsonl (ChatML format)
- data/processed/val.jsonl (ChatML format)
- data/processed/test.jsonl (Benchmark format)
- data/processed/test.csv (Excel format có cột Model Output và Điểm đánh giá)
"""

import os
import csv
import json
import random

SYSTEM_PROMPT = (
    "Bạn là Trợ lý AI Tư vấn Pháp luật An toàn Giao thông đường bộ tại Việt Nam. "
    "Nhiệm vụ của bạn là giải đáp chính xác, rõ ràng các quy định, mức xử phạt và kỹ năng an toàn giao thông "
    "dựa trên căn cứ pháp lý hiện hành (Luật Trật tự, an toàn giao thông đường bộ 2024, Luật Đường bộ 2024, "
    "Nghị định 168/2024/NĐ-CP). Luôn giữ văn phong trang trọng, chuẩn mực và trích dẫn điều khoản cụ thể."
)

def main():
    raw_csv = os.path.join("data", "raw", "683_CauHoi_TTATGTDB.csv")
    out_dir = os.path.join("data", "processed")
    os.makedirs(out_dir, exist_ok=True)

    with open(raw_csv, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Loaded {len(rows)} samples from {raw_csv}")

    # Chuẩn hóa tên cột
    cleaned_rows = []
    for r in rows:
        stt = r.get("STT", "").strip()
        q = r.get("Câu hỏi", "").strip()
        # Tìm cột câu trả lời (có thể là 'Trả lời ' hoặc 'Trả lời')
        a = (r.get("Trả lời ", "") or r.get("Trả lời", "") or r.get("Câu trả lời", "")).strip()
        # Tìm cột nguồn
        src = (r.get(" Nguồn", "") or r.get("Nguồn", "") or r.get("Link", "")).strip()
        
        if q and a:
            cleaned_rows.append({
                "stt": stt,
                "question": q,
                "answer": a,
                "source": src
            })

    total = len(cleaned_rows)
    print(f"Valid Q&A pairs: {total}")

    # Phân tầng theo từng khối 10 câu (Stratified Chunk Sampling)
    # Khối 10 câu: 8 Train, 1 Val, 1 Test
    # Đảm bảo phân bố đồng đều từ STT 1 đến STT 700
    random.seed(42)

    train_data = []
    val_data = []
    test_data = []

    chunk_size = 10
    for i in range(0, total, chunk_size):
        chunk = cleaned_rows[i:i + chunk_size]
        indices = list(range(len(chunk)))
        random.shuffle(indices)
        
        if len(chunk) == chunk_size:
            # 8 cho train, 1 cho val, 1 cho test
            test_idx = indices[0]
            val_idx = indices[1]
            train_indices = indices[2:]
            
            test_data.append(chunk[test_idx])
            val_data.append(chunk[val_idx])
            for tidx in train_indices:
                train_data.append(chunk[tidx])
        else:
            # Xử lý phần dư cuối cùng (~3 câu)
            # Ưu tiên đưa vào train để đảm bảo tỷ lệ 80%
            for c_item in chunk:
                train_data.append(c_item)

    print(f"Split results:")
    print(f"- Train set : {len(train_data)} ({len(train_data)/total*100:.2f}%)")
    print(f"- Val set   : {len(val_data)} ({len(val_data)/total*100:.2f}%)")
    print(f"- Test set  : {len(test_data)} ({len(test_data)/total*100:.2f}%)")

    # 1. Xuất data/processed/train.jsonl
    train_jsonl_path = os.path.join(out_dir, "train.jsonl")
    with open(train_jsonl_path, mode="w", encoding="utf-8") as f:
        for item in train_data:
            entry = {
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": item["question"]},
                    {"role": "assistant", "content": item["answer"]}
                ]
            }
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # 2. Xuất data/processed/val.jsonl
    val_jsonl_path = os.path.join(out_dir, "val.jsonl")
    with open(val_jsonl_path, mode="w", encoding="utf-8") as f:
        for item in val_data:
            entry = {
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": item["question"]},
                    {"role": "assistant", "content": item["answer"]}
                ]
            }
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # 3. Xuất data/processed/test.jsonl
    test_jsonl_path = os.path.join(out_dir, "test.jsonl")
    with open(test_jsonl_path, mode="w", encoding="utf-8") as f:
        for idx, item in enumerate(test_data, 1):
            entry = {
                "id": f"TEST_{idx:03d}",
                "stt": item["stt"],
                "question": item["question"],
                "ground_truth": item["answer"],
                "source": item["source"]
            }
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    # 4. Xuất data/processed/test.csv (UTF-8 BOM cho Excel)
    test_csv_path = os.path.join(out_dir, "test.csv")
    csv_fields = [
        "ID",
        "STT_Gốc",
        "Câu hỏi",
        "Đáp án chuẩn (Ground Truth)",
        "Nguồn tham chiếu",
        "Câu trả lời của Mô hình (Model Output)",
        "Điểm đánh giá"
    ]
    with open(test_csv_path, mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=csv_fields)
        writer.writeheader()
        for idx, item in enumerate(test_data, 1):
            writer.writerow({
                "ID": f"TEST_{idx:03d}",
                "STT_Gốc": item["stt"],
                "Câu hỏi": item["question"],
                "Đáp án chuẩn (Ground Truth)": item["answer"],
                "Nguồn tham chiếu": item["source"],
                "Câu trả lời của Mô hình (Model Output)": "",
                "Điểm đánh giá": ""
            })

    print(f"\nSuccessfully generated all dataset splits in '{out_dir}':")
    print(f"1. {train_jsonl_path}")
    print(f"2. {val_jsonl_path}")
    print(f"3. {test_jsonl_path}")
    print(f"4. {test_csv_path}")

if __name__ == "__main__":
    main()
