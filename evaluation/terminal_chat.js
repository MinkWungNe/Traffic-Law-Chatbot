/**
 * Module: terminal_chat.js
 * Mục đích: Giao diện Chatbot & Kiểm thử tương tác trực tiếp trên Terminal bằng Node.js.
 * Thay thế cho giao diện Streamlit Web cũ, tối ưu kiểm thử nhanh trên dòng lệnh.
 * Người phụ trách: Thành viên 4 (Evaluation Lead)
 */

const readline = require('readline');

// Bảng màu ANSI trực quan
const CYAN = '\x1b[96m';
const GREEN = '\x1b[92m';
const YELLOW = '\x1b[93m';
const BLUE = '\x1b[94m';
const RED = '\x1b[91m';
const GRAY = '\x1b[90m';
const BOLD = '\x1b[1m';
const RESET = '\x1b[0m';

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8000';

function printBanner() {
  console.clear();
  console.log(`${CYAN}${'='.repeat(78)}${RESET}`);
  console.log(`${BOLD}${YELLOW}   🚦 CHATBOT AI TƯ VẤN LUẬT GIAO THÔNG ĐƯỜNG BỘ (TERMINAL INTERFACE) 🚦${RESET}`);
  console.log(`${CYAN}${'='.repeat(78)}${RESET}`);
  console.log(`  ${GRAY}Kết nối Backend:${RESET} ${BLUE}${BACKEND_URL}${RESET}`);
  console.log(`  ${GRAY}Gõ câu hỏi pháp luật giao thông hoặc dùng các lệnh hỗ trợ:${RESET}`);
  console.log(`  ${BOLD}:help${RESET} (Hướng dẫn) | ${BOLD}:status${RESET} (Kiểm tra Backend) | ${BOLD}:clear${RESET} (Xóa màn hình) | ${BOLD}:exit${RESET} (Thoát)`);
  console.log(`${CYAN}${'='.repeat(78)}${RESET}\n`);
}

async function checkHealth() {
  let timeout;
  try {
    const controller = new AbortController();
    timeout = setTimeout(() => controller.abort(), 3000);
    const res = await fetch(`${BACKEND_URL}/api/health`, { signal: controller.signal });
    if (res.ok) {
      const data = await res.json();
      console.log(`\n${GREEN}✔ [KẾT NỐI OK] Backend đang hoạt động:${RESET} ${data.message || 'Hệ thống sẵn sàng'}\n`);
    } else {
      console.log(`\n${YELLOW}⚠ [CẢNH BÁO] Backend phản hồi mã lỗi: ${res.status}${RESET}\n`);
    }
  } catch (err) {
    console.log(`\n${RED}✖ [NGOẠI TUYẾN] Không thể kết nối tới Backend tại ${BACKEND_URL}${RESET}`);
    console.log(`  ${GRAY}Bạn có thể chạy backend bằng: python -m uvicorn backend.src.api.main:app --reload${RESET}\n`);
  } finally {
    if (timeout) clearTimeout(timeout);
  }
}

async function sendQuery(query) {
  const startTime = Date.now();
  process.stdout.write(`${YELLOW}⏳ Đang tra cứu căn cứ pháp lý và tổng hợp câu trả lời...${RESET}\r`);

  let timeout;
  try {
    const controller = new AbortController();
    timeout = setTimeout(() => controller.abort(), 30000);

    const res = await fetch(`${BACKEND_URL}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, top_k: 3, temperature: 0.2 }),
      signal: controller.signal
    });

    const latency = Date.now() - startTime;
    process.stdout.write(' '.repeat(70) + '\r'); // Xóa dòng chờ

    if (res.ok) {
      const data = await res.json();
      console.log(`\n${BOLD}${GREEN}🤖 TRỢ LÝ AI LUẬT GIAO THÔNG:${RESET} ${GRAY}(Phản hồi trong ${latency}ms)${RESET}`);
      console.log(`${data.answer}\n`);

      if (data.sources && data.sources.length > 0) {
        console.log(`${BOLD}${CYAN}📚 CĂN CỨ PHÁP LÝ TRÍCH DẪN:${RESET}`);
        data.sources.forEach((src, idx) => {
          const scoreStr = src.score !== undefined && src.score !== null ? ` [Độ khớp: ${(src.score * 100).toFixed(1)}%]` : '';
          console.log(`  ${BOLD}${idx + 1}. ${src.title}${scoreStr}${RESET}`);
          if (src.snippet) {
            console.log(`     ${GRAY}${src.snippet.trim()}${RESET}`);
          }
        });
        console.log('');
      }
    } else {
      console.log(`\n${RED}⚠️ Lỗi từ máy chủ Backend (Mã lỗi: ${res.status})${RESET}\n`);
    }
  } catch (err) {
    process.stdout.write(' '.repeat(70) + '\r');
    console.log(`\n${YELLOW}⚠️ [CHẾ ĐỘ MOCK KIỂM THỬ NGOẠI TUYẾN]${RESET}`);
    console.log(`  ${GRAY}(FastAPI Backend chưa chạy tại ${BACKEND_URL}. Phản hồi giả lập để kiểm thử luồng terminal):${RESET}`);
    console.log(`  ${BOLD}🤖 Trả lời:${RESET} Đối với câu hỏi "${query}", theo quy định tại Nghị định 168/2024/NĐ-CP và Luật Trật tự ATGT đường bộ 2024, người tham gia giao thông cần chấp hành đúng biển báo hiệu, vạch kẻ đường và hiệu lệnh CSGT.`);
    console.log(`  ${CYAN}📚 Căn cứ tham khảo:${RESET} Nghị định 168/2024/NĐ-CP; Luật TTATGTĐB 36/2024/QH15.\n`);
  } finally {
    if (timeout) clearTimeout(timeout);
  }
}

function startCLI() {
  printBanner();

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
    prompt: `${BOLD}${BLUE}Người dùng > ${RESET}`
  });

  rl.prompt();

  rl.on('line', async (line) => {
    const input = line.trim();

    if (!input) {
      rl.prompt();
      return;
    }

    if (input === ':exit' || input === ':quit') {
      console.log(`\n${GREEN}Cảm ơn bạn đã sử dụng Chatbot AI Luật Giao Thông. Tạm biệt!${RESET}\n`);
      rl.close();
      process.exit(0);
    }

    if (input === ':clear') {
      printBanner();
      rl.prompt();
      return;
    }

    if (input === ':status') {
      await checkHealth();
      rl.prompt();
      return;
    }

    if (input === ':help') {
      console.log(`\n${BOLD}${CYAN}DANH SÁCH LỆNH HỖ TRỢ:${RESET}`);
      console.log(`  ${BOLD}:status${RESET}     - Kiểm tra kết nối tới FastAPI Backend`);
      console.log(`  ${BOLD}:clear${RESET}      - Xóa trắng màn hình console`);
      console.log(`  ${BOLD}:exit/:quit${RESET} - Thoát chương trình`);
      console.log(`  ${BOLD}<câu hỏi>${RESET}   - Nhập bất kỳ câu hỏi nào để chatbot tra cứu luật\n`);
      rl.prompt();
      return;
    }

    await sendQuery(input);
    rl.prompt();
  });

  rl.on('close', () => {
    process.exit(0);
  });
}

if (require.main === module) {
  startCLI();
}

module.exports = { sendQuery, checkHealth };
