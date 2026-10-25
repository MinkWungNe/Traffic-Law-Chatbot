/**
 * Module: test_terminal.js
 * Mục đích: Bộ kiểm thử tự động (Unit Test & Integration Test) chạy trực tiếp trên Terminal bằng Node.js.
 * Cho phép kiểm tra toàn diện phân hệ Đánh giá & RAG thông qua lệnh: `npm test`.
 * Người phụ trách: Thành viên 4 (Evaluation Lead)
 */

const fs = require('fs');
const path = require('path');
const {
  extractLegalCitations,
  parseCSV,
  retrieveDocuments,
  calculateMetricsForQuery
} = require('./benchmark');

// Bảng màu ANSI
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
const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

let passedTests = 0;
let failedTests = 0;

function assert(condition, testName, errMsg) {
  if (condition) {
    console.log(`  ${GREEN}✔ [PASSED]${RESET} ${testName}`);
    passedTests++;
  } else {
    console.log(`  ${RED}✖ [FAILED]${RESET} ${testName}: ${errMsg}`);
    failedTests++;
  }
}

async function runTestSuite() {
  console.clear();
  console.log(`${CYAN}${'='.repeat(78)}${RESET}`);
  console.log(`${BOLD}${YELLOW}   🧪 BỘ KIỂM THỬ TỰ ĐỘNG PHÂN HỆ EVALUATION & TESTING (TERMINAL) 🧪${RESET}`);
  console.log(`${CYAN}${'='.repeat(78)}${RESET}\n`);

  // --- KỊCH BẢN 1: BÓC TÁCH CĂN CỨ PHÁP LÝ BẰNG REGEX ---
  console.log(`${BOLD}${BLUE}Kịch bản 1: Kiểm tra trích xuất căn cứ pháp lý tự động (Regex Extraction)${RESET}`);
  const sampleText =
    'Căn cứ Điều 6 Nghị định số 168/2024/NĐ-CP và Thông tư số 79/2024/TT-BCA ' +
    'quy định xử phạt theo Luật Trật tự, an toàn giao thông đường bộ.';
  const citations = extractLegalCitations(sampleText);

  assert(citations.includes('Điều 6'), 'Trích xuất Điều luật', "Không tìm thấy 'Điều 6'");
  assert(citations.includes('Nghị định 168/2024/NĐ-CP'), 'Trích xuất Nghị định', "Không tìm thấy 'Nghị định 168/2024/NĐ-CP'");
  assert(citations.includes('Thông tư 79/2024/TT-BCA'), 'Trích xuất Thông tư', "Không tìm thấy 'Thông tư 79/2024/TT-BCA'");
  assert(citations.some(c => /Luật Trật tự/i.test(c)), 'Trích xuất tên Luật', "Không tìm thấy Luật Trật tự ATGT đường bộ");

  // --- KỊCH BẢN 2: NẠP VÀ LÀM SẠCH TẬP 683 CÂU HỎI CSV ---
  console.log(`\n${BOLD}${BLUE}Kịch bản 2: Kiểm tra nạp dữ liệu kiểm thử thực tế từ file CSV${RESET}`);
  const csvExists = fs.existsSync(DATASET_PATH);
  assert(csvExists, 'Kiểm tra tồn tại tệp 683_CauHoi_TTATGTDB.csv', `Không tìm thấy file tại ${DATASET_PATH}`);

  if (csvExists) {
    const csvContent = fs.readFileSync(DATASET_PATH, 'utf-8');
    const dataset = parseCSV(csvContent);
    assert(dataset.length === 683, 'Đọc đủ 683 câu hỏi chuẩn', `Kỳ vọng 683 câu, đọc được ${dataset.length}`);

    if (dataset.length > 0) {
      const first = dataset[0];
      assert(typeof first.id === 'number', 'Định dạng trường ID', 'Trường ID phải là số');
      assert(first.question && first.question.length > 0, 'Nội dung câu hỏi', 'Câu hỏi không được rỗng');
      assert(first.ground_truth_answer && first.ground_truth_answer.length > 0, 'Câu trả lời chuẩn', 'Đáp án chuẩn không được rỗng');
      assert(Array.isArray(first.ground_truth_citations), 'Danh sách căn cứ pháp lý', 'Citations phải là mảng');
    }
  }

  // --- KỊCH BẢN 3: TÍNH TOÁN CÁC CHỈ SỐ TOÁN HỌC (HIT, RECALL, MRR) ---
  console.log(`\n${BOLD}${BLUE}Kịch bản 3: Kiểm tra công thức toán học đo lường (Hit-rate@K, Recall@K, MRR)${RESET}`);
  const mockItem = {
    ground_truth_citations: ['Điều 6', 'Nghị định 168/2024/NĐ-CP'],
    ground_truth_answer: 'Quy định tại Điều 6 Nghị định 168/2024/NĐ-CP'
  };
  const mockRetrievedDocs = [
    { title: 'Trích lục Điều 6', snippet: 'Xử phạt người điều khiển xe mô tô.' },
    { title: 'Văn bản khác', snippet: 'Quy định chung.' },
    { title: 'Quy chuẩn', snippet: 'Biển báo hiệu.' }
  ];

  const metrics = calculateMetricsForQuery(mockItem, mockRetrievedDocs);
  assert(metrics.hit === 1.0, 'Đo lường Hit@K = 1.0', `Kỳ vọng 1.0, nhận ${metrics.hit}`);
  assert(metrics.recall === 0.5, 'Đo lường Recall@K = 0.5 (1/2)', `Kỳ vọng 0.5, nhận ${metrics.recall}`);
  assert(metrics.first_rank === 1, 'Xác định vị trí Rank đầu tiên = 1', `Kỳ vọng 1, nhận ${metrics.first_rank}`);
  assert(metrics.reciprocal_rank === 1.0, 'Đo lường MRR = 1.0 (1/1)', `Kỳ vọng 1.0, nhận ${metrics.reciprocal_rank}`);

  // --- KỊCH BẢN 4: TRUY XUẤT CÁC TÌNH HUỐNG THỰC TẾ ---
  console.log(`\n${BOLD}${BLUE}Kịch bản 4: Kiểm tra truy xuất Smart Lexical Retriever trên câu hỏi thực tế${RESET}`);
  const qRedLight = retrieveDocuments('Vượt đèn đỏ xe máy bị phạt bao nhiêu tiền?', 3);
  assert(
    qRedLight.some(d => d.title.includes('168/2024')),
    'Truy xuất câu hỏi Vượt đèn đỏ',
    'Phải tìm ra Nghị định 168/2024'
  );

  const qVehicleReg = retrieveDocuments('Thủ tục sang tên đổi chủ xe máy không chính chủ', 3);
  assert(
    qVehicleReg.some(d => d.title.includes('79/2024')),
    'Truy xuất câu hỏi Đăng ký/Sang tên xe',
    'Phải tìm ra Thông tư 79/2024'
  );

  // --- KỊCH BẢN 5: KIỂM TRA MÁY CHỦ BACKEND (NẾU ĐANG CHẠY) ---
  console.log(`\n${BOLD}${BLUE}Kịch bản 5: Kiểm tra kết nối dịch vụ Backend API${RESET}`);
  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 2000);
    const res = await fetch(`${BACKEND_URL}/api/health`, { signal: controller.signal });
    clearTimeout(timeout);
    if (res.ok) {
      assert(true, `Kết nối FastAPI Backend tại ${BACKEND_URL}`, 'Trực tuyến');
    } else {
      console.log(`  ${YELLOW}⚠ [CẢNH BÁO] Backend phản hồi trạng thái: ${res.status}${RESET}`);
    }
  } catch (err) {
    console.log(`  ${GRAY}ℹ [GHI CHÚ] Backend chưa khởi chạy (Kiểm thử hoạt động độc lập ở chế độ Offline/Isolated)${RESET}`);
  }

  // --- TỔNG KẾT KẾT QUẢ ---
  console.log(`\n${CYAN}${'='.repeat(78)}${RESET}`);
  if (failedTests === 0) {
    console.log(`${BOLD}${GREEN}✔ TẤT CẢ ${passedTests} KỊCH BẢN KIỂM THỬ ĐÃ ĐẠT CHUẨN XUẤT SẮC! [PASSED: 100%]${RESET}`);
  } else {
    console.log(`${BOLD}${RED}✖ KẾT QUẢ: ${passedTests} ĐẠT, ${failedTests} THẤT BẠI. CẦN KIỂM TRA LẠI MÃ NGUỒN!${RESET}`);
  }
  console.log(`${CYAN}${'='.repeat(78)}${RESET}\n`);

  process.exit(failedTests === 0 ? 0 : 1);
}

if (require.main === module) {
  runTestSuite();
}
