export interface FAQItem {
  id: string;
  topicId: "nongdocon" | "gplx" | "dentinhieu" | "tocdo" | "phatnguoi" | "caotoc" | "giayto";
  topicLabel: string;
  vehicleType: "xemay" | "oto" | "chung";
  vehicleLabel: string;
  question: string;
  fullAnswer: string;
  penaltyMoney: string;
  pointsDeducted: number;
  detentionDays?: string;
  lawCite: string;
  exceptions?: string;
  aiPrompts: string[];
  isSevere?: boolean;
}

export interface FAQTopic {
  id: string;
  label: string;
  iconName: string;
}

export const FAQ_TOPICS: FAQTopic[] = [
  {
    id: "all",
    label: "Tất cả tình huống",
    iconName: "Layers",
  },
  {
    id: "nongdocon",
    label: "Nồng độ cồn & Chất kích thích",
    iconName: "Wine",
  },
  {
    id: "gplx",
    label: "12 Điểm Giấy phép lái xe",
    iconName: "ShieldAlert",
  },
  {
    id: "dentinhieu",
    label: "Đèn tín hiệu & Quy tắc rẽ",
    iconName: "AlertTriangle",
  },
  {
    id: "tocdo",
    label: "Tốc độ & Khoảng cách an toàn",
    iconName: "Gauge",
  },
  {
    id: "phatnguoi",
    label: "Phạt nguội & Giám sát Camera",
    iconName: "Camera",
  },
  {
    id: "caotoc",
    label: "Quy tắc Đường cao tốc",
    iconName: "Route",
  },
  {
    id: "giayto",
    label: "Đăng kiểm & Giấy tờ phương tiện",
    iconName: "FileText",
  },
];

export const FAQ_ITEMS: FAQItem[] = [
  // 1. NỒNG ĐỘ CỒN
  {
    id: "faq-ndc-01",
    topicId: "nongdocon",
    topicLabel: "Nồng độ cồn",
    vehicleType: "chung",
    vehicleLabel: "Ô tô & Xe máy",
    question: "Mức phạt nồng độ cồn kịch khung đối với ô tô và xe máy theo quy định mới nhất?",
    fullAnswer: "Khi người điều khiển phương tiện có nồng độ cồn vượt quá 80 miligam/100 mililít máu hoặc vượt quá 0,4 miligam/1 lít khí thở: Đối với xe ô tô: Phạt tiền từ 30.000.000đ - 40.000.000đ, trừ 10 điểm Giấy phép lái xe. Đối với xe mô tô, xe gắn máy: Phạt tiền từ 6.000.000đ - 8.000.000đ, trừ 10 điểm Giấy phép lái xe. Lực lượng chức năng có thẩm quyền tạm giữ phương tiện đến 07 ngày trước khi ra quyết định xử phạt.",
    penaltyMoney: "Ô tô: 30 - 40 triệu đ | Xe máy: 6 - 8 triệu đ",
    pointsDeducted: 10,
    detentionDays: "Tạm giữ xe đến 07 ngày",
    lawCite: "Điểm a Khoản 10, Điểm d Khoản 16 Điều 6 (Ô tô) và Điểm e Khoản 8, Điểm g Khoản 12 Điều 7 (Xe máy) Nghị định 168/2024/NĐ-CP.",
    exceptions: "Nếu từ chối kiểm tra nồng độ cồn của lực lượng CSGT đang thi hành công vụ, người điều khiển sẽ bị xử phạt ở mức kịch khung cao nhất.",
    aiPrompts: [
      "Quy trình đo lại nồng độ cồn và yêu cầu xét nghiệm máu khi nghi ngờ kết quả?",
      "Người ngồi cùng xe có bị xử phạt khi biết lái xe đã uống rượu bia không?",
    ],
    isSevere: true,
  },
  {
    id: "faq-ndc-02",
    topicId: "nongdocon",
    topicLabel: "Nồng độ cồn",
    vehicleType: "chung",
    vehicleLabel: "Toàn bộ phương tiện",
    question: "Uống thuốc siro ho hoặc ăn hoa quả lên men thổi cồn có bị xử phạt không?",
    fullAnswer: "Trường hợp người dân sử dụng thuốc chữa bệnh (như siro ho), thực phẩm hoặc trái cây lên men sinh ra cồn sinh học trong hơi thở: Người điều khiển có quyền đề nghị CSGT cho nghỉ ngơi từ 10 - 15 phút, uống nước lọc rồi đo lại. Nếu máy vẫn báo chỉ số, người dân có quyền yêu cầu được xét nghiệm máu tại cơ sở y tế gần nhất. Kết quả định lượng cồn trong máu là căn cứ pháp lý cao nhất để bác bỏ vi phạm.",
    penaltyMoney: "Không xử phạt (nếu xét nghiệm máu âm tính)",
    pointsDeducted: 0,
    lawCite: "Thông tư 73/2024/TT-BCA và quy chế đối thoại giải trình theo Luật Xử lý vi phạm hành chính.",
    exceptions: "Cần giữ lại đơn thuốc, nhãn thuốc hoặc hóa đơn thực phẩm để làm căn cứ giải trình văn bản với Đội CSGT lập biên bản.",
    aiPrompts: [
      "Mẫu đơn đề nghị xét nghiệm máu xác minh nồng độ cồn tự nhiên?",
      "Chi phí xét nghiệm máu do bên nào chi trả nếu kết quả không có cồn?",
    ],
    isSevere: false,
  },
  {
    id: "faq-ndc-03",
    topicId: "nongdocon",
    topicLabel: "Nồng độ cồn",
    vehicleType: "xemay",
    vehicleLabel: "Xe máy",
    question: "Nồng độ cồn mức 1 (chưa vượt quá 0.25 mg/lít khí thở) đối với xe máy phạt bao nhiêu?",
    fullAnswer: "Điều khiển xe mô tô, xe gắn máy trên đường mà trong máu hoặc hơi thở có nồng độ cồn nhưng chưa vượt quá 50 mg/100 ml máu hoặc chưa vượt quá 0,25 mg/1 lít khí thở: Phạt tiền từ 2.000.000đ đến 3.000.000đ; Trừ 02 điểm Giấy phép lái xe; Tạm giữ xe đến 07 ngày.",
    penaltyMoney: "2.000.000đ - 3.000.000đ",
    pointsDeducted: 2,
    detentionDays: "Tạm giữ xe đến 07 ngày",
    lawCite: "Điểm c Khoản 6, Điểm a Khoản 12 Điều 7 Nghị định 168/2024/NĐ-CP.",
    aiPrompts: [
      "Uống 1 cốc bia thì sau bao lâu hết nồng độ cồn trong hơi thở?",
      "Nồng độ cồn mức 1 có bị giam xe máy tại chỗ không?",
    ],
    isSevere: false,
  },

  // 2. 12 ĐIỂM GIẤY PHÉP LÁI XE
  {
    id: "faq-gplx-01",
    topicId: "gplx",
    topicLabel: "12 Điểm GPLX",
    vehicleType: "chung",
    vehicleLabel: "Quy chế chung",
    question: "Cơ chế quản lý 12 điểm Giấy phép lái xe theo Luật TTATGTĐB 2024 hoạt động thế nào?",
    fullAnswer: "Theo Điều 58 Luật Trật tự, an toàn giao thông đường bộ số 36/2024/QH15: Mỗi Giấy phép lái xe có 12 điểm. Khi vi phạm pháp luật về giao thông, người lái xe sẽ bị trừ điểm vào hệ thống dữ liệu điện tử quốc gia. Nếu GPLX chưa bị trừ hết điểm và không bị trừ điểm trong thời hạn 12 tháng kể từ ngày bị trừ điểm gần nhất thì được phục hồi đủ 12 điểm. Dữ liệu điểm được cập nhật tự động lên tài khoản VNeID.",
    penaltyMoney: "Trừ điểm tự động trên hệ thống dữ liệu VNeID",
    pointsDeducted: 0,
    lawCite: "Điều 58 Luật Trật tự, an toàn giao thông đường bộ số 36/2024/QH15.",
    exceptions: "Nếu trong thời hạn 12 tháng lại có hành vi vi phạm bị trừ điểm thì thời hạn tính lại từ ngày có quyết định trừ điểm mới.",
    aiPrompts: [
      "Làm thế nào để kiểm tra số điểm còn lại của bằng lái trên VNeID?",
      "Có bị mất bằng lái vật lý khi bị trừ điểm không?",
    ],
    isSevere: false,
  },
  {
    id: "faq-gplx-02",
    topicId: "gplx",
    topicLabel: "12 Điểm GPLX",
    vehicleType: "chung",
    vehicleLabel: "Người có GPLX",
    question: "Khi bị trừ hết toàn bộ 12 điểm Giấy phép lái xe thì phải làm gì để được lái xe trở lại?",
    fullAnswer: "Giấy phép lái xe bị trừ hết điểm thì người có GPLX không được điều khiển phương tiện tham gia giao thông. Sau thời hạn ít nhất là 06 tháng kể từ ngày bị trừ hết điểm, người có GPLX được tham gia kiểm tra nội dung kiến thức pháp luật về trật tự, an toàn giao thông đường bộ do lực lượng CSGT tổ chức; nếu kết quả đạt yêu cầu thì được phục hồi đủ 12 điểm.",
    penaltyMoney: "Cấm lái xe cho đến khi sát hạch đạt yêu cầu",
    pointsDeducted: 12,
    lawCite: "Khoản 3 Điều 58 Luật Trật tự, an toàn giao thông đường bộ số 36/2024/QH15.",
    exceptions: "Nếu tiếp tục lái xe khi GPLX đã bị trừ hết điểm sẽ bị xử phạt như hành vi không có Giấy phép lái xe hợp lệ.",
    aiPrompts: [
      "Thủ tục đăng ký kiểm tra kiến thức phục hồi điểm GPLX gồm những gì?",
      "Lái xe khi hết điểm GPLX bị phạt bao nhiêu tiền?",
    ],
    isSevere: true,
  },

  // 3. ĐÈN TÍN HIỆU & QUY TẮC RẼ
  {
    id: "faq-den-01",
    topicId: "dentinhieu",
    topicLabel: "Đèn tín hiệu",
    vehicleType: "xemay",
    vehicleLabel: "Xe máy",
    question: "Xe máy rẽ phải khi đèn đỏ không có biển báo phụ thì bị phạt bao nhiêu và có trừ điểm không?",
    fullAnswer: "Rẽ phải khi đèn đỏ chỉ được phép khi có: (1) Hiệu lệnh của CSGT điều tiết; (2) Đèn tín hiệu phụ hình mũi tên màu xanh chỉ hướng rẽ phải; hoặc (3) Biển phụ cho phép 'Đèn đỏ được phép rẽ phải'. Nếu không có các tín hiệu trên, hành vi rẽ phải bị coi là không chấp hành hiệu lệnh của đèn tín hiệu giao thông (vượt đèn đỏ). Mức phạt: 800.000đ - 1.000.000đ, trừ 02 điểm GPLX.",
    penaltyMoney: "800.000đ - 1.000.000đ",
    pointsDeducted: 2,
    lawCite: "Điểm e Khoản 4, Điểm a Khoản 12 Điều 7 Nghị định 168/2024/NĐ-CP.",
    exceptions: "Nếu có cảnh sát giao thông đứng trực tiếp vẫy xe rẽ phải thì hiệu lệnh của CSGT luôn có giá trị ưu tiên cao nhất, người dân rẽ theo hiệu lệnh không bị phạt.",
    aiPrompts: [
      "Có được bật xi nhan rẽ phải khi đèn đỏ nếu không có biển báo không?",
      "Biển phụ cho phép rẽ phải có áp dụng cho xe ba gác không?",
    ],
    isSevere: false,
  },
  {
    id: "faq-den-02",
    topicId: "dentinhieu",
    topicLabel: "Đèn tín hiệu",
    vehicleType: "oto",
    vehicleLabel: "Ô tô",
    question: "Ô tô vượt đèn đỏ hoặc đèn vàng bị phạt bao nhiêu tiền và trừ mấy điểm bằng lái?",
    fullAnswer: "Người điều khiển xe ô tô không chấp hành hiệu lệnh của đèn tín hiệu giao thông (bao gồm cả hành vi vượt đèn đỏ và cố tình tăng tốc vượt đèn vàng khi chưa vào nút giao) bị phạt tiền từ 4.000.000đ đến 6.000.000đ. Đồng thời, bị trừ 03 điểm Giấy phép lái xe. Nếu hành vi vượt đèn dẫn đến tai nạn giao thông, mức phạt sẽ tăng nặng và bị trừ 10 điểm GPLX.",
    penaltyMoney: "4.000.000đ - 6.000.000đ",
    pointsDeducted: 3,
    lawCite: "Điểm a Khoản 5, Điểm b Khoản 16 Điều 6 Nghị định 168/2024/NĐ-CP.",
    exceptions: "Trường hợp phương tiện đã vượt qua vạch dừng xe trước khi đèn chuyển sang màu vàng thì được phép tiếp tục đi tiếp mà không bị coi là vượt đèn.",
    aiPrompts: [
      "Vượt đèn vàng thế nào thì không bị phạt?",
      "Camera phạt nguội ghi nhận ô tô vượt đèn đỏ như thế nào?",
    ],
    isSevere: true,
  },

  // 4. TỐC ĐỘ & KHOẢNG CÁCH
  {
    id: "faq-td-01",
    topicId: "tocdo",
    topicLabel: "Tốc độ",
    vehicleType: "chung",
    vehicleLabel: "Ô tô & Xe máy",
    question: "Chạy quá tốc độ quy định từ 10 km/h đến 20 km/h bị xử phạt thế nào?",
    fullAnswer: "Hành vi điều khiển phương tiện chạy quá tốc độ quy định từ 10 km/h đến 20 km/h: - Đối với xe ô tô: Phạt tiền từ 4.000.000đ đến 6.000.000đ; Trừ 02 điểm Giấy phép lái xe. - Đối với xe mô tô, xe gắn máy: Phạt tiền từ 800.000đ đến 1.000.000đ; Trừ 02 điểm Giấy phép lái xe.",
    penaltyMoney: "Ô tô: 4 - 6 triệu đ | Xe máy: 800k - 1 triệu đ",
    pointsDeducted: 2,
    lawCite: "Điểm i Khoản 5 Điều 6 (Ô tô) và Điểm a Khoản 4 Điều 7 (Xe máy) Nghị định 168/2024/NĐ-CP.",
    aiPrompts: [
      "Chạy quá tốc độ dưới 5 km/h có bị bắn tốc độ phạt không?",
      "Khoảng cách an toàn tối thiểu theo tốc độ trên cao tốc quy định ra sao?",
    ],
    isSevere: false,
  },
  {
    id: "faq-td-02",
    topicId: "tocdo",
    topicLabel: "Tốc độ",
    vehicleType: "oto",
    vehicleLabel: "Ô tô",
    question: "Chạy quá tốc độ trên 35 km/h đối với xe ô tô mức phạt kịch khung ra sao?",
    fullAnswer: "Điều khiển xe ô tô chạy quá tốc độ quy định trên 35 km/h là hành vi vi phạm đặc biệt nghiêm trọng đe dọa an toàn giao thông đường bộ. Mức xử phạt tiền từ 12.000.000đ đến 14.000.000đ; Đồng thời bị trừ 06 điểm Giấy phép lái xe. Nếu gây tai nạn giao thông sẽ bị trừ 10 điểm GPLX và tịch thu phương tiện nếu có dấu hiệu đua xe trái phép.",
    penaltyMoney: "12.000.000đ - 14.000.000đ",
    pointsDeducted: 6,
    lawCite: "Điểm c Khoản 9, Điểm c Khoản 16 Điều 6 Nghị định 168/2024/NĐ-CP.",
    aiPrompts: [
      "Bắn tốc độ ban đêm không có đèn đường thì hình ảnh có giá trị phạt nguội không?",
      "Quy định về tem kiểm định máy đo tốc độ của CSGT?",
    ],
    isSevere: true,
  },

  // 5. PHẠT NGUỘI & GIÁM SÁT
  {
    id: "faq-pn-01",
    topicId: "phatnguoi",
    topicLabel: "Phạt nguội",
    vehicleType: "chung",
    vehicleLabel: "Chủ xe & Người thuê xe",
    question: "Cho người khác mượn hoặc thuê xe tự lái bị phạt nguội thì ai phải nộp phạt?",
    fullAnswer: "Căn cứ Khoản 8 Điều 47 Nghị định 168/2024/NĐ-CP: Khi phát hiện vi phạm qua camera phạt nguội, CSGT sẽ gửi thông báo đến chủ phương tiện. Chủ xe có nghĩa vụ phối hợp để xác định người điều khiển phương tiện. Nếu chủ xe là cá nhân hoặc tổ chức cho thuê xe xuất trình được Hợp đồng thuê xe, biên bản bàn giao xe và giấy tờ tùy thân của người thuê thì cơ quan Công an sẽ lập biên bản xử phạt đối với người trực tiếp lái xe, chủ xe không phải nộp thay.",
    penaltyMoney: "Người điều khiển thực tế chịu phạt",
    pointsDeducted: 0,
    lawCite: "Khoản 8 Điều 47 Nghị định 168/2024/NĐ-CP và Nghị định 61/2026/NĐ-CP.",
    exceptions: "Nếu chủ phương tiện không hợp tác giải trình hoặc không chứng minh được người lái, chủ phương tiện sẽ bị xử phạt vi phạm hành chính đối với hành vi đó.",
    aiPrompts: [
      "Mẫu đơn giải trình chuyển phạt nguội cho người thuê xe tự lái?",
      "Sau bao nhiêu ngày thì thông tin phạt nguội bị chặn đăng kiểm?",
    ],
    isSevere: false,
  },
  {
    id: "faq-pn-02",
    topicId: "phatnguoi",
    topicLabel: "Phạt nguội",
    vehicleType: "chung",
    vehicleLabel: "Công dân toàn quốc",
    question: "Quy trình tra cứu và nộp phạt nguội trực tuyến trên Cổng Dịch vụ công Quốc gia?",
    fullAnswer: "Bước 1: Tra cứu vi phạm trên Cổng TTĐT Cục CSGT (www.csgt.vn) hoặc mục 'Giao thông' trên app VNeID. Bước 2: Khi nhận được Mã quyết định xử phạt (qua SMS/VNeID hoặc thông báo giấy), truy cập Cổng Dịch vụ công Quốc gia (dichvucong.gov.vn). Bước 3: Nhập Mã quyết định xử phạt, chọn ngân hàng thanh toán trực tuyến. Sau khi thanh toán thành công, hệ thống tự động xóa cảnh báo vi phạm trên hệ thống Đăng kiểm.",
    penaltyMoney: "Nộp đúng mức phạt ghi trong quyết định (miễn phí xử lý DVC)",
    pointsDeducted: 0,
    lawCite: "Thông tư 15/2022/TT-BCA và quy chế nộp phạt điện tử Cổng DVC Quốc gia.",
    aiPrompts: [
      "Tại sao đã nộp phạt nguội online mà trên web CSGT vẫn chưa cập nhật?",
      "Quy trình xóa cảnh báo đăng kiểm xe sau khi nộp phạt nguội?",
    ],
    isSevere: false,
  },

  // 6. QUY TẮC ĐƯỜNG CAO TỐC
  {
    id: "faq-ct-01",
    topicId: "caotoc",
    topicLabel: "Đường cao tốc",
    vehicleType: "oto",
    vehicleLabel: "Ô tô",
    question: "Chạy lùi hoặc đi ngược chiều trên đường cao tốc bị xử phạt bao nhiêu?",
    fullAnswer: "Người điều khiển xe ô tô lùi xe trên đường cao tốc hoặc đi ngược chiều trên đường cao tốc bị phạt tiền từ 30.000.000đ đến 40.000.000đ. Đồng thời, bị trừ 10 điểm Giấy phép lái xe. Hành vi này được xem là một trong những lỗi nguy hiểm nhất đe dọa trực tiếp đến tính mạng của nhiều phương tiện tham gia giao thông tốc độ cao.",
    penaltyMoney: "30.000.000đ - 40.000.000đ",
    pointsDeducted: 10,
    lawCite: "Điểm d Khoản 11, Điểm d Khoản 16 Điều 6 Nghị định 168/2024/NĐ-CP.",
    exceptions: "Trường hợp xe gặp sự cố kỹ thuật khẩn cấp và việc lùi xe được thực hiện dưới sự chỉ dẫn của nhân viên trạm thu phí/lực lượng chức năng điều tiết thì không bị xử phạt theo tình thế cấp thiết (Điều 11 Luật XLVPHC).",
    aiPrompts: [
      "Sự cố xe hỏng làn thu phí cao tốc có được miễn phạt lùi xe không?",
      "Trách nhiệm hình sự nếu đi ngược chiều cao tốc gây tai nạn giao thông?",
    ],
    isSevere: true,
  },
  {
    id: "faq-ct-02",
    topicId: "caotoc",
    topicLabel: "Đường cao tốc",
    vehicleType: "oto",
    vehicleLabel: "Ô tô",
    question: "Dừng xe, đỗ xe trên làn dừng khẩn cấp đường cao tốc không đúng quy định phạt bao nhiêu?",
    fullAnswer: "Người lái xe ô tô chỉ được dừng, đỗ xe trên làn dừng khẩn cấp khi xe gặp sự cố kỹ thuật không thể di chuyển được hoặc trong tình trạng khẩn cấp. Hành vi dừng, đỗ xe trên làn dừng xe khẩn cấp của đường cao tốc không đúng quy định (như dừng đi vệ sinh, ngủ, chụp ảnh) bị phạt tiền từ 10.000.000đ đến 12.000.000đ và bị trừ 03 điểm GPLX.",
    penaltyMoney: "10.000.000đ - 12.000.000đ",
    pointsDeducted: 3,
    lawCite: "Điểm c Khoản 7, Điểm b Khoản 16 Điều 6 Nghị định 168/2024/NĐ-CP.",
    exceptions: "Khi buộc phải dừng khẩn cấp, lái xe phải bật ngay đèn cảnh báo nguy hiểm (hazard) và đặt biển/vật báo hiệu tam giác cách đuôi xe tối thiểu 150 mét.",
    aiPrompts: [
      "Quy định đặt vật cảnh báo an toàn khi xe chết máy trên cao tốc?",
      "Lái xe bị buồn ngủ có được tấp làn khẩn cấp chợp mắt không?",
    ],
    isSevere: true,
  },

  // 7. ĐĂNG KIỂM & GIẤY TỜ
  {
    id: "faq-gt-01",
    topicId: "giayto",
    topicLabel: "Giấy tờ xe",
    vehicleType: "oto",
    vehicleLabel: "Ô tô",
    question: "Xe ô tô quá hạn đăng kiểm trên 01 tháng bị phạt người lái và chủ xe ra sao?",
    fullAnswer: "Căn cứ Điểm b Khoản 6, Điểm a Khoản 13 Điều 13 và Điểm a Khoản 11 Điều 32 Nghị định 168/2024/NĐ-CP: - Đối với người trực tiếp điều khiển xe ô tô quá hạn đăng kiểm từ 01 tháng trở lên: Phạt tiền từ 4.000.000đ đến 6.000.000đ; Trừ 02 điểm GPLX. - Đối với chủ phương tiện: Phạt tiền từ 10.000.000đ đến 12.000.000đ (chủ xe cá nhân) hoặc từ 20.000.000đ đến 24.000.000đ (chủ xe là tổ chức/doanh nghiệp). Nếu chủ xe trực tiếp lái xe thì áp dụng chế tài phạt chủ xe.",
    penaltyMoney: "Lái xe: 4 - 6 triệu đ | Chủ xe: 10 - 24 triệu đ",
    pointsDeducted: 2,
    lawCite: "Điều 13 & Điều 32 Nghị định 168/2024/NĐ-CP.",
    aiPrompts: [
      "Đang trên đường đi đến trung tâm đăng kiểm bị CSGT dừng xe có bị phạt quá hạn không?",
      "Trễ hạn đăng kiểm dưới 1 tháng thì mức phạt chênh lệch bao nhiêu?",
    ],
    isSevere: true,
  },
  {
    id: "faq-gt-02",
    topicId: "giayto",
    topicLabel: "Giấy tờ xe",
    vehicleType: "chung",
    vehicleLabel: "Toàn bộ người lái",
    question: "Đã xuất trình Giấy phép lái xe và Đăng ký xe trên VNeID có cần mang bản cứng không?",
    fullAnswer: "Theo Thông tư 73/2024/TT-BCA và Luật Trật tự, an toàn giao thông đường bộ 36/2024/QH15: Khi các thông tin về Giấy phép lái xe, Đăng ký xe, Giấy chứng nhận bảo hiểm bắt buộc đã được tích hợp, cập nhật và hiển thị trên ứng dụng định danh quốc gia VNeID thì thông tin đó có giá trị tương đương việc kiểm tra trực tiếp các giấy tờ bản giấy. CSGT thực hiện kiểm tra, đối soát thông tin qua thiết bị nghiệp vụ kết nối CSDL dân cư và giao thông.",
    penaltyMoney: "Không bị xử phạt lỗi không mang giấy tờ",
    pointsDeducted: 0,
    lawCite: "Khoản 3 Điều 56 Luật 36/2024/QH15 và Điều 12 Thông tư 73/2024/TT-BCA.",
    exceptions: "Nếu hệ thống VNeID gặp sự cố mạng hoặc chưa tích hợp thành công mà không có bản giấy thì vẫn có thể bị lập biên bản nhắc nhở hoặc xử lý.",
    aiPrompts: [
      "Cách xuất trình giấy tờ xe trên VNeID khi không có sóng 4G?",
      "CSGT có được quyền giữ điện thoại của người dân khi kiểm tra VNeID không?",
    ],
    isSevere: false,
  },
];
