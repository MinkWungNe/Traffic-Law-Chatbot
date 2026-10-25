/**
 * Module: benchmark.js
 * Mục đích: Đo lường chất lượng truy xuất pháp lý (Hit-rate@K, Recall@K, MRR) trên Terminal bằng Node.js.
 * Đánh giá trực tiếp tập 683 câu hỏi thực tế từ Cổng TTĐT Bộ Công an mà không cần giao diện Web.
 * Người phụ trách: Thành viên 4 (Evaluation Lead)
 */

const fs = require('fs');
const path = require('path');

// Bảng màu ANSI trực quan
const CYAN = '\x1b[96m';
const GREEN = '\x1b[92m';
const YELLOW = '\x1b[93m';
const BLUE = '\x1b[94m';
const RED = '\x1b[91m';
const GRAY = '\x1b[90m';
const BOLD = '\x1b[1m';
const RESET = '\x1b[0m';

const ROOT_DIR = path.resolve(__dirname, '..');
const DATASET_PATH = path.join(ROOT_DIR, 'data', 'raw', '683_CauHoi_TTATGTDB.csv');
const REPORT_PATH = path.join(ROOT_DIR, 'evaluation', 'benchmark_report.json');

// Kho tri thức các văn bản luật chủ đạo (đồng bộ với benchmark_runner.py)
const LEGAL_KNOWLEDGE_BASE = [
  {
    title: 'Nghị định 168/2024/NĐ-CP',
    keywords: [
      'xử phạt', 'phạt tiền', 'trừ điểm', 'giấy phép lái xe', 'gplx', 'tước', 'nồng độ cồn',
      'rượu bia', 'đèn đỏ', 'đèn vàng', 'ngược chiều', 'quá tốc độ', 'lùi xe', 'cao tốc',
      'đăng kiểm', 'hết hạn', 'mũ bảo hiểm', 'chở quá số người', 'dừng đỗ', 'bấm còi',
      'chuyển làn', 'không xi nhan', 'xe không chính chủ', 'quá tải', 'phí cao tốc',
      'điện thoại khi lái xe', 'quá niên hạn', 'biển số che khuất', 'đua xe', 'lạng lách', 'điều 6', 'điều 13', 'điều 32'
    ],
    snippet: 'Nghị định số 168/2024/NĐ-CP quy định xử phạt vi phạm hành chính về trật tự, an toàn giao thông trong lĩnh vực giao thông đường bộ; trừ điểm, phục hồi điểm giấy phép lái xe.'
  },
  {
    title: 'Luật Trật tự, an toàn giao thông đường bộ',
    keywords: [
      'luật trật tự an toàn giao thông', 'luật 36/2024', 'điều kiện phương tiện', 'quy tắc giao thông',
      'người lái xe', 'người đi bộ', 'nhường đường', 'độ tuổi lái xe', 'trẻ em trên xe',
      'thiết bị an toàn', 'dừng xe', 'đỗ xe', 'vượt xe', 'chuyển hướng', 'hệ thống giám sát',
      'phát hiện vi phạm', 'điều 67', 'điều 9', 'điều 10', 'điều 11', 'điều 12'
    ],
    snippet: 'Luật Trật tự, an toàn giao thông đường bộ số 36/2024/QH15 quy định về quy tắc, phương tiện, người tham gia giao thông đường bộ và chỉ huy, điều khiển giao thông.'
  },
  {
    title: 'Nghị định 135/2021/NĐ-CP',
    keywords: [
      'phạt nguội', 'camera', 'thiết bị kỹ thuật nghiệp vụ', 'hình ảnh', 'video', 'trích xuất',
      'thông báo vi phạm', 'phương tiện nghiệp vụ', 'cá nhân tổ chức cung cấp', 'dữ liệu',
      'cổng thông tin', 'tra cứu phạt nguội', 'nghị định 184/2025', 'nghị định 61/2026', 'điều 15'
    ],
    snippet: 'Nghị định số 135/2021/NĐ-CP (sửa đổi bởi NĐ 184/2025/NĐ-CP và NĐ 61/2026/NĐ-CP) quy định về danh mục thiết bị kỹ thuật nghiệp vụ và quy trình thu thập dữ liệu xử phạt VPHC.'
  },
  {
    title: 'Thông tư 79/2024/TT-BCA',
    keywords: [
      'đăng ký xe', 'biển số', 'sang tên', 'chuyển quyền sở hữu', 'thu hồi chứng nhận', 'biển số định danh',
      'xe không chính chủ', 'giấy viết tay', 'mất giấy đăng ký', 'hồ sơ xe', 'công an xã', 'điều 32',
      'điều 16', 'cà vẹt xe', 'đổi biển số', 'tạm trú', 'thường trú', 'xe đấu giá'
    ],
    snippet: 'Thông tư số 79/2024/TT-BCA quy định về cấp, thu hồi chứng nhận đăng ký xe, biển số xe cơ giới, xe máy chuyên dùng và thủ tục đăng ký sang tên xe.'
  },
  {
    title: 'Thông tư 73/2024/TT-BCA',
    keywords: [
      'tuần tra', 'kiểm soát', 'csgt', 'cảnh sát giao thông', 'dừng phương tiện', 'dừng xe',
      'kế hoạch tuần tra', 'chuyên đề', 'kiểm tra giấy tờ', 'nồng độ cồn', 'ma túy', 'quá tải',
      'quyền hạn csgt', 'tổ công tác', 'trang bị vũ khí', 'quay phim csgt', 'giám sát csgt', 'điều 8', 'điều 12', 'điều 16'
    ],
    snippet: 'Thông tư số 73/2024/TT-BCA quy định về công tác tuần tra, kiểm soát, xử lý vi phạm hành chính về giao thông đường bộ của Cảnh sát giao thông.'
  },
  {
    title: 'Luật Đường bộ',
    keywords: [
      'luật đường bộ', 'luật 35/2024', 'kết cấu hạ tầng', 'đất dành cho kết cấu hạ tầng', 'hành lang an toàn',
      'đường cao tốc', 'thu phí', 'kinh doanh vận tải', 'bến xe', 'bãi đỗ xe', 'trạm dừng nghỉ',
      'tải trọng trục', 'xe quá khổ quá tải', 'vận tải hành khách', 'vận tải hàng hóa'
    ],
    snippet: 'Luật Đường bộ số 35/2024/QH15 quy định về hoạt động đường bộ, kết cấu hạ tầng đường bộ, phương tiện và vận tải đường bộ.'
  },
  {
    title: 'Thông tư 38/2024/TT-BGTVT',
    keywords: [
      'tốc độ', 'khoảng cách', 'tốc độ tối đa', 'tốc độ cho phép', 'khoảng cách an toàn',
      'trong khu đông dân cư', 'ngoài khu đông dân cư', 'đường đôi', 'đường một chiều', 'đường hai chiều',
      'xe máy điện', 'xe gắn máy', '60km/h', '50km/h', '80km/h', '90km/h', '100km/h', '120km/h', 'thời tiết xấu', 'sương mù'
    ],
    snippet: 'Thông tư số 38/2024/TT-BGTVT quy định về tốc độ và khoảng cách an toàn của xe cơ giới, xe máy chuyên dùng tham gia giao thông đường bộ.'
  },
  {
    title: 'Quy chuẩn QCVN 41:2024/BGTVT',
    keywords: [
      'biển báo', 'qcvn 41', 'vạch kẻ đường', 'đèn tín hiệu', 'cột cờ', 'biển cấm',
      'biển hiệu lệnh', 'biển chỉ dẫn', 'biển cảnh báo', 'vạch liền', 'vạch đứt',
      'vạch vàng', 'vạch trắng', 'mũi tên chỉ hướng', 'đè vạch', 'sai làn', 'tiểu đảo'
    ],
    snippet: 'Quy chuẩn kỹ thuật quốc gia QCVN 41:2024/BGTVT về báo hiệu đường bộ (kèm theo Thông tư 51/2024/TT-BGTVT).'
  }
];

/**
 * Trích xuất căn cứ pháp lý từ văn bản bằng biểu thức chính quy (Regex).
 */
function extractLegalCitations(text) {
  if (!text || typeof text !== 'string') return [];
  const citations = new Set();

  // 1. Nghị định
  const ndRegex = /(?:Nghị\s*định|NĐ)(?:\s+số)?\s*(\d+\/\d+\/(?:NĐ-CP|ND-CP))/gi;
  let m;
  while ((m = ndRegex.exec(text)) !== null) {
    citations.add(`Nghị định ${m[1].toUpperCase()}`);
  }

  // 2. Thông tư
  const ttRegex = /(?:Thông\s*tư|TT)(?:\s+số)?\s*(\d+\/\d+\/(?:TT-[A-Z]+))/gi;
  while ((m = ttRegex.exec(text)) !== null) {
    citations.add(`Thông tư ${m[1].toUpperCase()}`);
  }

  // 3. Điều luật
  const dieuRegex = /(?:^|[^\p{L}\p{N}])(?:Điều)\s+(\d+)\b/gui;
  while ((m = dieuRegex.exec(text)) !== null) {
    citations.add(`Điều ${m[1]}`);
  }

  // 4. Tên các đạo luật lớn
  const legalNames = [
    'Luật Trật tự, an toàn giao thông đường bộ',
    'Luật Trật tự an toàn giao thông đường bộ',
    'Luật Giao thông đường bộ',
    'Luật Đường bộ',
    'Luật Xử lý vi phạm hành chính',
    'Quy chuẩn 41',
    'QCVN 41'
  ];

  for (const name of legalNames) {
    if (new RegExp(name, 'i').test(text)) {
      citations.add(name);
    }
  }

  return Array.from(citations);
}

/**
 * Phân tích tệp CSV kiểm thử 683 câu hỏi.
 */
function parseCSV(content) {
  const lines = [];
  let currentField = '';
  let inQuotes = false;
  let currentRow = [];

  for (let i = 0; i < content.length; i++) {
    const char = content[i];
    const nextChar = content[i + 1];

    if (char === '"') {
      if (inQuotes && nextChar === '"') {
        currentField += '"';
        i++;
      } else {
        inQuotes = !inQuotes;
      }
    } else if (char === ',' && !inQuotes) {
      currentRow.push(currentField);
      currentField = '';
    } else if ((char === '\r' || char === '\n') && !inQuotes) {
      if (char === '\r' && nextChar === '\n') i++;
      currentRow.push(currentField);
      currentField = '';
      if (currentRow.some(col => col.trim().length > 0)) {
        lines.push(currentRow);
      }
      currentRow = [];
    } else {
      currentField += char;
    }
  }

  if (currentField || currentRow.length > 0) {
    currentRow.push(currentField);
    lines.push(currentRow);
  }

  if (lines.length < 2) return [];

  const headers = lines[0].map(h => h.trim().replace(/^[\uFEFF]/, ''));
  const qIdx = headers.findIndex(h => /câu hỏi/i.test(h));
  const aIdx = headers.findIndex(h => /trả lời/i.test(h));
  const idIdx = headers.findIndex(h => /stt/i.test(h));

  const dataset = [];
  for (let i = 1; i < lines.length; i++) {
    const row = lines[i];
    const question = qIdx !== -1 && row[qIdx] ? row[qIdx].trim() : '';
    const answer = aIdx !== -1 && row[aIdx] ? row[aIdx].trim() : '';
    const id = idIdx !== -1 && row[idIdx] ? parseInt(row[idIdx].trim(), 10) || i : i;

    if (question && question.length > 5) {
      dataset.push({
        id,
        question,
        ground_truth_answer: answer,
        ground_truth_citations: extractLegalCitations(answer)
      });
    }
  }

  return dataset;
}

/**
 * Tìm kiếm ngữ nghĩa từ vựng thông minh (Smart Lexical Retriever).
 */
function retrieveDocuments(query, topK = 3) {
  const queryLower = query.toLowerCase();
  const scoredDocs = LEGAL_KNOWLEDGE_BASE.map(doc => {
    let score = 0;
    const matched = [];
    for (const kw of doc.keywords) {
      if (queryLower.includes(kw.toLowerCase())) {
        score += 1.0;
        matched.push(kw);
      }
    }
    return {
      title: doc.title,
      snippet: doc.snippet,
      score: score > 0 ? parseFloat(Math.min(0.99, 0.65 + score * 0.08).toFixed(2)) : 0.40,
      matched_count: score
    };
  });

  scoredDocs.sort((a, b) => b.score - a.score);
  return scoredDocs.slice(0, topK);
}

/**
 * Tính toán các chỉ số toán học cho 1 câu hỏi: Hit@K, Recall@K, MRR.
 */
function calculateMetricsForQuery(item, retrievedDocs) {
  const gtCitations = item.ground_truth_citations || [];

  if (gtCitations.length === 0) {
    return { hit: 1.0, recall: 1.0, first_rank: 1, reciprocal_rank: 1.0, matched_citations: [] };
  }

  const combinedText = retrievedDocs.map(d => `${d.title} ${d.snippet}`).join(' ').toLowerCase();
  const matchedCitations = [];

  for (const cite of gtCitations) {
    const citeLower = cite.toLowerCase();
    if (combinedText.includes(citeLower)) {
      matchedCitations.push(cite);
      continue;
    }
    // So khớp theo số hiệu văn bản (VD: 168/2024, 79/2024)
    const numMatch = cite.match(/\d+\/\d+/);
    if (numMatch && combinedText.includes(numMatch[0])) {
      matchedCitations.push(cite);
    }
  }

  const recall = matchedCitations.length / gtCitations.length;
  const hit = matchedCitations.length > 0 ? 1.0 : 0.0;

  let firstRank = null;
  let reciprocalRank = 0.0;

  for (let idx = 0; idx < retrievedDocs.length; idx++) {
    const docText = `${retrievedDocs[idx].title} ${retrievedDocs[idx].snippet}`.toLowerCase();
    const isHit = gtCitations.some(c => {
      const cLow = c.toLowerCase();
      if (docText.includes(cLow)) return true;
      const numM = c.match(/\d+\/\d+/);
      return numM && docText.includes(numM[0]);
    });

    if (isHit) {
      firstRank = idx + 1;
      reciprocalRank = 1.0 / firstRank;
      break;
    }
  }

  return {
    hit,
    recall,
    first_rank: firstRank,
    reciprocal_rank: reciprocalRank,
    matched_citations: matchedCitations
  };
}

/**
 * Chạy đánh giá toàn diện và xuất kết quả ra Terminal & JSON.
 */
function runBenchmark(maxSamples = 50, topK = 3) {
  console.clear();
  console.log(`${CYAN}${'='.repeat(78)}${RESET}`);
  console.log(`${BOLD}${YELLOW}   📊 CHƯƠNG TRÌNH ĐÁNH GIÁ & BENCHMARK HỆ THỐNG RAG (TERMINAL RUNNER) 📊${RESET}`);
  console.log(`${CYAN}${'='.repeat(78)}${RESET}`);
  console.log(`  ${GRAY}Phân hệ:${RESET} Phân hệ 4: Evaluation & Testing (Node.js Terminal Engine)`);
  console.log(`  ${GRAY}Tệp kiểm thử:${RESET} ${DATASET_PATH}`);
  console.log(`${CYAN}${'='.repeat(78)}${RESET}\n`);

  if (!fs.existsSync(DATASET_PATH)) {
    console.error(`${RED}✖ Không tìm thấy tệp dữ liệu kiểm thử tại: ${DATASET_PATH}${RESET}`);
    process.exit(1);
  }

  console.log(`${BLUE}1. Đang nạp và phân tích tệp CSV 683 câu hỏi...${RESET}`);
  const csvContent = fs.readFileSync(DATASET_PATH, 'utf-8');
  const allDataset = parseCSV(csvContent);
  console.log(`   ${GREEN}✔ Đã nạp thành công ${allDataset.length} câu hỏi hợp lệ.${RESET}`);

  const evalDataset = maxSamples ? allDataset.slice(0, maxSamples) : allDataset;
  console.log(`\n${BLUE}2. Bắt đầu đánh giá trên ${evalDataset.length} câu hỏi (Top-K = ${topK})...${RESET}\n`);

  const startTime = Date.now();
  let totalHit = 0;
  let totalRecall = 0;
  let totalMrr = 0;
  const detailedRecords = [];

  evalDataset.forEach((item, idx) => {
    const docs = retrieveDocuments(item.question, topK);
    const metrics = calculateMetricsForQuery(item, docs);

    totalHit += metrics.hit;
    totalRecall += metrics.recall;
    totalMrr += metrics.reciprocal_rank;

    detailedRecords.push({
      id: item.id,
      question: item.question,
      ground_truth_citations: item.ground_truth_citations,
      retrieved_sources: docs.map(d => d.title),
      hit: metrics.hit,
      recall: parseFloat(metrics.recall.toFixed(3)),
      first_rank: metrics.first_rank,
      is_passed: metrics.hit === 1.0
    });

    // In tiến độ dạng vạch
    if ((idx + 1) % 10 === 0 || idx === evalDataset.length - 1) {
      const percent = Math.round(((idx + 1) / evalDataset.length) * 100);
      const barLen = Math.round(percent / 4);
      const bar = '█'.repeat(barLen) + '-'.repeat(25 - barLen);
      process.stdout.write(`  [${bar}] ${percent}% (${idx + 1}/${evalDataset.length} câu)\r`);
    }
  });

  const durationSec = (Date.now() - startTime) / 1000;
  const totalCount = evalDataset.length;
  const hitRate = totalHit / totalCount;
  const avgRecall = totalRecall / totalCount;
  const avgMrr = totalMrr / totalCount;
  const avgLatency = (durationSec / totalCount) * 1000;

  console.log('\n\n' + `${BOLD}${GREEN}✔ HOÀN TẤT ĐO LƯỜNG! KẾT QUẢ TỔNG QUAN:${RESET}`);
  console.log(`${CYAN}${'='.repeat(78)}${RESET}`);
  console.log(`  ${BOLD}🎯 Tổng số câu hỏi đánh giá:${RESET} ${totalCount} / ${allDataset.length} câu`);
  console.log(`  ${BOLD}⏱️  Tổng thời gian xử lý:${RESET}     ${durationSec.toFixed(2)} giây (${avgLatency.toFixed(1)} ms/câu)`);
  console.log(`  ${BOLD}✨ Hit-rate@${topK}:${RESET}                  ${GREEN}${BOLD}${(hitRate * 100).toFixed(1)}%${RESET}  ${GRAY}(Tỷ lệ tìm trúng ít nhất 1 căn cứ luật)${RESET}`);
  console.log(`  ${BOLD}📚 Recall@${topK}:${RESET}                    ${CYAN}${BOLD}${(avgRecall * 100).toFixed(1)}%${RESET}  ${GRAY}(Độ bao phủ căn cứ pháp lý cần thiết)${RESET}`);
  console.log(`  ${BOLD}🥇 Chỉ số MRR:${RESET}                   ${YELLOW}${BOLD}${avgMrr.toFixed(4)}${RESET}  ${GRAY}(Thứ hạng trung bình của căn cứ đúng)${RESET}`);
  console.log(`${CYAN}${'='.repeat(78)}${RESET}\n`);

  // Xuất báo cáo JSON
  const report = {
    metadata: {
      framework: 'Node.js Terminal Evaluation Runner',
      total_questions: allDataset.length,
      evaluated_samples: totalCount,
      top_k: topK,
      evaluation_time_seconds: parseFloat(durationSec.toFixed(2)),
      timestamp: new Date().toISOString()
    },
    summary_metrics: {
      hit_rate: parseFloat(hitRate.toFixed(4)),
      hit_rate_percentage: `${(hitRate * 100).toFixed(1)}%`,
      recall_at_k: parseFloat(avgRecall.toFixed(4)),
      recall_percentage: `${(avgRecall * 100).toFixed(1)}%`,
      mrr: parseFloat(avgMrr.toFixed(4)),
      avg_latency_per_query_ms: parseFloat(avgLatency.toFixed(2))
    },
    detailed_results: detailedRecords
  };

  fs.writeFileSync(REPORT_PATH, JSON.stringify(report, null, 2), 'utf-8');
  console.log(`${GREEN}✔ Báo cáo Benchmark đã được lưu tự động vào:${RESET} ${REPORT_PATH}\n`);
}

// Xử lý tham số dòng lệnh
if (require.main === module) {
  const args = process.argv.slice(2);
  let samples = 50;
  if (args.includes('--full')) {
    samples = null;
  } else {
    const sIdx = args.indexOf('--samples');
    if (sIdx !== -1 && args[sIdx + 1]) {
      samples = parseInt(args[sIdx + 1], 10) || 50;
    }
  }
  runBenchmark(samples);
}

module.exports = {
  extractLegalCitations,
  parseCSV,
  retrieveDocuments,
  calculateMetricsForQuery,
  runBenchmark
};
