/**
 * ==============================================================================
 * NOTE KIẾN TRÚC ĐỒ ÁN (ARCHITECTURAL DECISION):
 * Danh mục 22 văn bản pháp luật giao thông đường bộ được nạp tĩnh tại Client (Frontend)
 * nhằm tối ưu tốc độ phản hồi tức thì (Zero Latency) và giữ kiến trúc phân hệ tinh gọn,
 * tập trung toàn bộ tài nguyên Backend cho RAG Core, Vector DB và suy luận AI Chatbot.
 * ==============================================================================
 */

export interface RelatedDocItem {
  relationType: "goc" | "sua_doi";
  title: string;
  number: string;
  sourceUrl: string;
}

export interface LegalDocItem {
  id: string;
  category: "luat" | "nghi-dinh" | "thong-tu" | "quy-chuan";
  typeLabel: string;
  title: string;
  number: string;
  date: string;
  effectiveDate?: string;
  status: string;
  desc: string;
  issuer: string;
  sourceUrl?: string;
  isConsolidated?: boolean;
  relatedDocs?: RelatedDocItem[];
  sampleAiPrompts?: string[];
}

export const LEGAL_DOCUMENTS: LegalDocItem[] = [
  {
    id: "doc-01",
    category: "luat",
    typeLabel: "Luật",
    title: "Luật Trật tự, an toàn giao thông đường bộ",
    number: "Số 55/VBHN-VPQH",
    date: "27/06/2024",
    effectiveDate: "01/01/2025",
    status: "Còn hiệu lực",
    issuer: "Quốc hội",
    desc: "Luật quy định toàn diện về quy tắc giao thông đường bộ, điều kiện phương tiện, người lái xe, chỉ huy điều khiển giao thông và giải quyết tai nạn giao thông trên phạm vi cả nước. Điểm nhấn cốt lõi là thiết lập cơ chế 12 điểm giấy phép lái xe (GPLX) với quy trình trừ điểm, phục hồi điểm tự động sau 12 tháng không vi phạm, đồng thời phân hạng lại hệ thống GPLX tương thích chuẩn quốc tế. Đạo luật này duy trì nghiêm ngặt nguyên tắc cấm tuyệt đối điều khiển phương tiện khi có nồng độ cồn trong máu hoặc hơi thở, đồng thời siết chặt quy chuẩn an toàn cho trẻ em trên ô tô và xe đưa đón học sinh. Văn bản có hiệu lực từ ngày 01/01/2025, chính thức thay thế các quy định về trật tự, an toàn giao thông của Luật Giao thông đường bộ năm 2008.",
    sourceUrl: "https://congbao.chinhphu.vn/van-ban/van-ban-hop-nhat-so-55-vbhn-vpqh-469185/63695.htm",
    isConsolidated: true,
    sampleAiPrompts: [
      "Tóm tắt các điểm mới quan trọng nhất của Luật Trật tự ATGT đường bộ 36/2024/QH15",
      "Quy chế trừ điểm và phục hồi điểm bằng lái xe 12 điểm hoạt động như thế nào?",
      "Trẻ em ngồi trên ô tô phải tuân thủ điều kiện an toàn nào theo Luật 36/2024?"
    ],
    relatedDocs: [
      {
        relationType: "goc",
        title: "Luật Trật tự, an toàn giao thông đường bộ",
        number: "Số 36/2024/QH15",
        sourceUrl: "https://congbao.chinhphu.vn/van-ban/luat-so-36-2024-qh15-42555.htm"
      },
      {
        relationType: "sua_doi",
        title: "Luật sửa đổi, bổ sung một số điều của 10 Luật có liên quan đến an ninh, trật tự",
        number: "Số 118/2025/QH15",
        sourceUrl: "https://congbao.chinhphu.vn/van-ban/luat-so-118-2025-qh15-468680.htm"
      }
    ]
  },
  {
    id: "doc-02",
    category: "luat",
    typeLabel: "Bộ luật",
    title: "Bộ luật Hình sự",
    number: "Số 135/VBHN-VPQH",
    date: "27/11/2015",
    effectiveDate: "01/01/2018",
    status: "Còn hiệu lực",
    issuer: "Quốc hội",
    desc: "Bộ luật quy định các tội phạm và chế tài hình sự nghiêm khắc đối với các hành vi xâm phạm an toàn giao thông đường bộ gây hậu quả nghiêm trọng về người và tài sản. Trong lĩnh vực giao thông, văn bản xác lập trách nhiệm hình sự trực tiếp đối với tội vi phạm quy định về tham gia giao thông đường bộ (Điều 260), hành vi giao xe cho người không đủ điều kiện điều khiển (Điều 264) và tội cản trở giao thông đường bộ (Điều 261). Mức phạt tù có thể lên tới 15 năm đối với các trường hợp vi phạm có nồng độ cồn, không có giấy phép lái xe hoặc gây tai nạn làm chết từ 03 người trở lên. Văn bản hợp nhất kế thừa Bộ luật Hình sự 2015 và Luật sửa đổi năm 2017, có hiệu lực thi hành đồng bộ từ ngày 01/01/2018.",
    sourceUrl: "https://congbao.chinhphu.vn/van-ban/van-ban-hop-nhat-so-135-vbhn-vpqh-46165/58885.htm",
    isConsolidated: true,
    sampleAiPrompts: [
      "Khung hình phạt tội vi phạm quy định tham gia giao thông theo Điều 260 Bộ luật Hình sự?",
      "Giao xe máy cho người chưa đủ tuổi hoặc đã uống rượu gây tai nạn có bị đi tù không?"
    ],
    relatedDocs: [
      {
        relationType: "goc",
        title: "Bộ luật Hình sự",
        number: "Số 100/2015/QH13",
        sourceUrl: "https://congbao.chinhphu.vn/van-ban/luat-so-100-2015-qh13-18442.htm"
      },
      {
        relationType: "sua_doi",
        title: "Luật sửa đổi, bổ sung một số điều của Bộ luật Hình sự",
        number: "Số 12/2017/QH14",
        sourceUrl: "https://congbao.chinhphu.vn/van-ban/luat-so-12-2017-qh14-24289/18538.htm"
      }
    ]
  },
  {
    id: "doc-03",
    category: "luat",
    typeLabel: "Bộ luật",
    title: "Bộ luật Dân sự",
    number: "Số 91/2015/QH13",
    date: "24/11/2015",
    effectiveDate: "01/01/2017",
    status: "Còn hiệu lực",
    issuer: "Quốc hội",
    desc: "Bộ luật xác lập nguyên tắc bồi thường thiệt hại ngoài hợp đồng phát sinh từ tai nạn giao thông, áp dụng đối với chủ sở hữu và người trực tiếp điều khiển phương tiện. Theo Điều 601, phương tiện giao thông vận tải cơ giới được phân loại là nguồn nguy hiểm cao độ, buộc chủ sở hữu hoặc người chiếm hữu hợp pháp phải bồi thường thiệt hại ngay cả khi không có lỗi, trừ trường hợp bất khả kháng hoặc lỗi hoàn toàn do nạn nhân. Văn bản cũng quy định chi tiết phạm vi bồi thường bao gồm chi phí cứu chữa, tổn thất thu nhập thực tế, chi phí mai táng và khoản bù đắp tổn thất về tinh thần cho thân nhân người bị nạn. Bộ luật được Quốc hội khóa XIII thông qua và có hiệu lực thi hành kể từ ngày 01/01/2017.",
    sourceUrl: "https://congbao.chinhphu.vn/van-ban/luat-so-91-2015-qh13-18397.htm",
    sampleAiPrompts: [
      "Trách nhiệm bồi thường thiệt hại do nguồn nguy hiểm cao độ theo Điều 601 Bộ luật Dân sự?",
      "Chủ xe cho mượn xe gây tai nạn thì ai phải bồi thường dân sự?"
    ]
  },
  {
    id: "doc-04",
    category: "luat",
    typeLabel: "Luật",
    title: "Luật Xử lý vi phạm hành chính",
    number: "Số 90/VBHN-VPQH",
    date: "20/06/2012",
    effectiveDate: "01/01/2022",
    status: "Còn hiệu lực",
    issuer: "Quốc hội",
    desc: "Đạo luật này là nền tảng pháp lý cao nhất điều chỉnh quy trình, thẩm quyền và hình thức xử phạt vi phạm hành chính của các lực lượng chức năng, bao gồm Cảnh sát giao thông và Thanh tra giao thông. Văn bản quy định chặt chẽ thủ tục lập biên bản vi phạm, mức phạt tiền tối đa, thời hiệu xử phạt, cùng các biện pháp ngăn chặn như tạm giữ phương tiện, giấy phép lái xe và niêm phong tang vật. Cơ chế cưỡng chế thi hành quyết định xử phạt, giải quyết khiếu nại, tố cáo và nguyên tắc bảo đảm quyền giải trình của người vi phạm cũng được luật hóa chi tiết. Bản hợp nhất cập nhật Luật sửa đổi, bổ sung năm 2020, chính thức có hiệu lực thi hành từ ngày 01/01/2022.",
    sourceUrl: "https://congbao.chinhphu.vn/van-ban/van-ban-hop-nhat-so-90-vbhn-vpqh-469265.htm",
    isConsolidated: true,
    sampleAiPrompts: [
      "Quy định tạm giữ xe máy, ô tô tối đa bao nhiêu ngày theo Luật Xử lý VPHC?",
      "Thời hiệu xử phạt vi phạm hành chính giao thông là bao lâu?"
    ],
    relatedDocs: [
      {
        relationType: "goc",
        title: "Luật Xử lý vi phạm hành chính",
        number: "Số 15/2012/QH13",
        sourceUrl: "https://congbao.chinhphu.vn/van-ban/luat-so-15-2012-qh13-915/11323.htm"
      },
      {
        relationType: "sua_doi",
        title: "Luật sửa đổi, bổ sung một số điều của Luật Xử lý vi phạm hành chính",
        number: "Số 67/2020/QH14",
        sourceUrl: "https://congbao.chinhphu.vn/van-ban/nghi-quyet-so-67-2020-qh14-32691/33729.htm"
      }
    ]
  },
  {
    id: "doc-05",
    category: "luat",
    typeLabel: "Luật",
    title: "Luật Phòng, chống tác hại của rượu, bia",
    number: "Số 44/2019/QH14",
    date: "14/06/2019",
    effectiveDate: "01/01/2020",
    status: "Còn hiệu lực",
    issuer: "Quốc hội",
    desc: "Luật quy định các biện pháp kiểm soát việc sử dụng, giảm thiểu tác hại và trách nhiệm của cơ quan, tổ chức, cá nhân trong phòng, chống tác hại của rượu, bia. Điểm tác động trực tiếp và sâu rộng nhất tới người tham gia giao thông là Khoản 6 Điều 5, nghiêm cấm tuyệt đối hành vi điều khiển phương tiện giao thông mà trong máu hoặc hơi thở có nồng độ cồn ở bất kỳ mức độ nào (chính sách Zero Tolerance). Quy định này là căn cứ pháp lý cốt lõi để các nghị định xử phạt giao thông thiết lập mức phạt kịch khung và tước giấy phép lái xe đối với tài xế vi phạm cồn. Luật có hiệu lực thi hành từ ngày 01/01/2020 và là bước ngoặt quan trọng hình thành thói quen 'đã uống rượu bia, không lái xe' trong xã hội.",
    sourceUrl: "https://congbao.chinhphu.vn/van-ban/luat-so-44-2019-qh14-29251.htm",
    sampleAiPrompts: [
      "Luật Phòng chống tác hại rượu bia quy định thế nào về việc lái xe sau khi uống bia?",
      "Ép người khác uống rượu bia rồi để họ lái xe có bị phạt không?"
    ]
  },
  {
    id: "doc-06",
    category: "luat",
    typeLabel: "Luật",
    title: "Luật Đường bộ",
    number: "Số 49/VBHN-VPQH",
    date: "27/06/2024",
    effectiveDate: "01/01/2025",
    status: "Còn hiệu lực",
    issuer: "Quốc hội",
    desc: "Luật Đường bộ quy định về quy hoạch, đầu tư xây dựng, quản lý, vận hành khai thác, bảo trì và bảo vệ kết cấu hạ tầng giao thông đường bộ, cũng như hoạt động vận tải đường bộ. Văn bản phân định rõ các cấp đường bộ, quy chuẩn hành lang an toàn giao thông, cơ chế thu phí sử dụng đường cao tốc do Nhà nước đầu tư và các yêu cầu kỹ thuật đối với trạm dừng nghỉ. Luật đồng thời hoàn thiện khung pháp lý về quản lý xe hợp đồng, xe buýt, xe taxi công nghệ, siết chặt điều kiện an toàn đối với phương tiện vận chuyển hành khách và hàng hóa siêu trường, siêu trọng. Luật được tách ra từ Luật Giao thông đường bộ 2008 và có hiệu lực thi hành từ ngày 01/01/2025.",
    sourceUrl: "https://congbao.chinhphu.vn/van-ban/van-ban-hop-nhat-so-49-vbhn-vpqh-469134/63485.htm",
    isConsolidated: true,
    relatedDocs: [
      {
        relationType: "goc",
        title: "Luật Đường bộ",
        number: "Số 35/2024/QH15",
        sourceUrl: "https://congbao.chinhphu.vn/van-ban/luat-so-35-2024-qh15-42568.htm",
      },
      {
        relationType: "sua_doi",
        title: "Luật sửa đổi, bổ sung một số điều của 10 Luật có liên quan đến an ninh, trật tự",
        number: "Số 118/2025/QH15",
        sourceUrl: "https://congbao.chinhphu.vn/van-ban/luat-so-118-2025-qh15-468680/61578.htm",
      },
    ],
    sampleAiPrompts: [
      "Luật Đường bộ 2024 khác gì so với Luật Giao thông đường bộ 2008 trước đây?"
    ],
  },
  {
    id: "doc-07",
    category: "luat",
    typeLabel: "Luật",
    title: "Luật Đường sắt",
    number: "Số 75/VBHN-VPQH",
    date: "27/06/2025",
    effectiveDate: "01/01/2026",
    status: "Còn hiệu lực",
    issuer: "Quốc hội",
    desc: "Luật điều chỉnh toàn bộ hoạt động quy hoạch, đầu tư, xây dựng, quản lý kết cấu hạ tầng, phương tiện giao thông đường sắt và an toàn giao thông đường sắt trên lãnh thổ Việt Nam. Đối với người tham gia giao thông đường bộ, luật thiết lập nguyên tắc quyền ưu tiên tuyệt đối của phương tiện đường sắt tại các điểm giao cắt cùng mức (đường ngang, lối đi tự mở) và ranh giới hành lang an toàn đường sắt. Văn bản tạo hành lang pháp lý mới để hiện đại hóa hệ thống đường sắt đô thị, đường sắt tốc độ cao Bắc - Nam và loại bỏ các điểm giao cắt nguy hiểm tiềm ẩn tai nạn. Luật có hiệu lực thi hành từ ngày 01/01/2026, thay thế toàn diện cho Luật Đường sắt năm 2017 trước đây.",
    sourceUrl: "https://congbao.chinhphu.vn/van-ban/van-ban-hop-nhat-so-75-vbhn-vpqh-469205.htm",
    isConsolidated: true,
    relatedDocs: [
      {
        relationType: "goc",
        title: "Luật Đường sắt",
        number: "Số 95/2025/QH15",
        sourceUrl: "https://congbao.chinhphu.vn/van-ban/luat-so-95-2025-qh15-45582.htm",
      },
      {
        relationType: "sua_doi",
        title: "Luật Quy hoạch",
        number: "Số 112/2025/QH15",
        sourceUrl: "https://congbao.chinhphu.vn/van-ban/luat-so-112-2025-qh15-468674.htm",
      },
      {
        relationType: "sua_doi",
        title: "Luật Xây dựng",
        number: "Số 135/2025/QH15",
        sourceUrl: "https://congbao.chinhphu.vn/van-ban/luat-so-135-2025-qh15-468695.htm",
      },
      {
        relationType: "sua_doi",
        title: "Luật Đầu tư",
        number: "Số 143/2025/QH15",
        sourceUrl: "https://congbao.chinhphu.vn/van-ban/luat-so-143-2025-qh15-468703.htm",
      },
    ],
    sampleAiPrompts: [
      "Quy định dừng xe tại đường ray tàu hỏa không có rào chắn như thế nào?"
    ],
    },
  {
    id: "doc-08",
    category: "luat",
    typeLabel: "Luật",
    title: "Luật Đo lường",
    number: "Số 73/VBHN-VPQH",
    date: "11/11/2011",
    effectiveDate: "01/07/2012",
    status: "Còn hiệu lực",
    issuer: "Quốc hội",
    desc: "Luật quy định về hoạt động đo lường, quyền và nghĩa vụ của tổ chức, cá nhân tham gia hoạt động đo lường, cũng như quản lý nhà nước về đo lường. Trong xử lý vi phạm giao thông, đạo luật này là cơ sở pháp lý kiểm định tính hợp pháp của các thiết bị kỹ thuật chuyên dụng của CSGT như máy đo nồng độ cồn, súng bắn tốc độ có ghi hình và cân tải trọng xe. Mọi phương tiện đo dùng để xử phạt vi phạm hành chính bắt buộc phải được kiểm định định kỳ, dán tem kiểm định hoặc có chứng chỉ kiểm định còn hiệu lực mới có giá trị pháp lý làm chứng cứ. Luật được Quốc hội khóa XIII thông qua ngày 11/11/2011 và có hiệu lực thi hành từ ngày 01/07/2012.",
    sourceUrl: "https://congbao.chinhphu.vn/van-ban/van-ban-hop-nhat-so-73-vbhn-vpqh-45875.htm",
    isConsolidated: true,
    sampleAiPrompts: [
      "Máy đo nồng độ cồn của CSGT phải có tem kiểm định như thế nào mới hợp lệ?"
    ],
    relatedDocs: [
      {
        relationType: "goc",
        title: "Luật Đo lường",
        number: "Số 04/2011/QH13",
        sourceUrl: "https://congbao.chinhphu.vn/van-ban/luat-so-04-2011-qh13-7028.htm"
      },
      {
        relationType: "sua_doi",
        title: "Luật sửa đổi, bổ sung một số điều của 37 Luật có liên quan đến quy hoạch",
        number: "Số 35/2018/QH14",
        sourceUrl: "https://congbao.chinhphu.vn/van-ban/nghi-quyet-so-35-2018-qh14-27813.htm"
      }
    ]
  },
  {
    id: "doc-09",
    category: "luat",
    typeLabel: "Luật",
    title: "Luật Cảnh vệ",
    number: "Số 04/VBHN-VPQH",
    date: "20/06/2017",
    effectiveDate: "01/01/2025",
    status: "Còn hiệu lực",
    issuer: "Quốc hội",
    desc: "Luật quy định về đối tượng cảnh vệ, biện pháp cảnh vệ, quyền hạn và trách nhiệm của lực lượng Cảnh vệ cùng các lực lượng phối hợp thuộc Bộ Công an và Bộ Quốc phòng. Đối với giao thông đường bộ, văn bản xác lập quyền ưu tiên tuyệt đối cho các đoàn xe cảnh vệ có Cảnh sát giao thông dẫn đường (xe phát tín hiệu còi, đèn ưu tiên, xe hộ tống). Mọi phương tiện tham gia giao thông khi gặp đoàn xe cảnh vệ bắt buộc phải giảm tốc độ, tấp sát lề đường bên phải hoặc dừng lại nhường đường, tuyệt đối không được cắt ngang đoàn xe. Bản hợp nhất cập nhật Luật sửa đổi năm 2024, có hiệu lực thi hành thống nhất từ ngày 01/01/2025.",
    sourceUrl: "https://congbao.chinhphu.vn/van-ban/van-ban-hop-nhat-so-04-vbhn-vpqh-468933.htm",
    isConsolidated: true,
    sampleAiPrompts: [
      "Không nhường đường cho đoàn xe CSGT dẫn đoàn cảnh vệ bị phạt bao nhiêu tiền?"
    ],
    relatedDocs: [
      {
        relationType: "goc",
        title: "Luật Cảnh vệ",
        number: "Số 13/2017/QH14",
        sourceUrl: "https://congbao.chinhphu.vn/van-ban/luat-so-13-2017-qh14-24273.htm"
      },
      {
        relationType: "sua_doi",
        title: "Luật sửa đổi, bổ sung một số điều của Luật Cảnh vệ",
        number: "Số 40/2024/QH15",
        sourceUrl: "https://congbao.chinhphu.vn/van-ban/luat-so-40-2024-qh15-42565.htm"
      },
      {
        relationType: "sua_doi",
        title: "Luật sửa đổi, bổ sung một số điều của 10 Luật có liên quan đến an ninh, trật tự",
        number: "Số 118/2025/QH15",
        sourceUrl: "https://congbao.chinhphu.vn/van-ban/luat-so-118-2025-qh15-468680.htm"
      }
    ]
  },
  {
    id: "doc-10",
    category: "nghi-dinh",
    typeLabel: "Nghị định",
    title: "Nghị định quy định xử phạt vi phạm hành chính TTATGT đường bộ; trừ, phục hồi điểm giấy phép lái xe.",
    number: "Số 168/2024/NĐ-CP",
    date: "26/12/2024",
    effectiveDate: "01/01/2025",
    status: "Còn hiệu lực",
    issuer: "Chính phủ",
    desc: "Nghị định quy định chi tiết hành vi vi phạm, hình thức xử phạt, mức phạt tiền, biện pháp khắc phục hậu quả và thủ tục trừ điểm, phục hồi điểm giấy phép lái xe trong lĩnh vực giao thông đường bộ. Văn bản thiết lập thang trừ điểm chi tiết từ 1 đến 12 điểm đối với các lỗi điển hình (như vượt đèn đỏ, chạy quá tốc độ, đi ngược chiều trên cao tốc), đồng thời nâng mức phạt tiền đối với các hành vi nguy hiểm có nguy cơ cao gây tai nạn. Nghị định bổ sung quy trình phục hồi tự động 12 điểm bằng lái sau 12 tháng không vi phạm hoặc qua kiểm tra kiến thức pháp luật khi bị trừ hết điểm. Nghị định có hiệu lực thi hành từ ngày 01/01/2025, thay thế Nghị định 100/2019/NĐ-CP và Nghị định 123/2021/NĐ-CP.",
    sourceUrl: "https://congbao.chinhphu.vn/van-ban/nghi-dinh-so-168-2024-nd-cp-43733.htm",
    sampleAiPrompts: [
      "Khung tiền phạt và mức trừ điểm GPLX khi vượt đèn đỏ theo Nghị định 168/2024?",
      "Chạy quá tốc độ trên cao tốc bị phạt bao nhiêu tiền và trừ mấy điểm GPLX?",
      "Những lỗi vi phạm nào bị trừ sạch 12 điểm giấy phép lái xe ngay lập tức?"
    ],
    relatedDocs: [
      {
        relationType: "goc",
        title: "Nghị định quy định xử phạt vi phạm hành chính TTATGT đường bộ; trừ, phục hồi điểm giấy phép lái xe.",
        number: "Số 168/2024/NĐ-CP",
        sourceUrl: "https://congbao.chinhphu.vn/van-ban/nghi-dinh-so-168-2024-nd-cp-43733.htm"
      },
      {
        relationType: "sua_doi",
        title: "Nghị định sửa đổi, bổ sung một số điều của Nghị định số 168/2024/NĐ-CP",
        number: "Số 238/2026/NĐ-CP",
        sourceUrl: "https://congbao.chinhphu.vn/van-ban/nghi-dinh-so-238-2026-nd-cp-469913/66580.htm"
      }
    ]
  },
  {
    id: "doc-11",
    category: "nghi-dinh",
    typeLabel: "Nghị định",
    title: "Nghị định quy định về danh mục, việc quản lý, sử dụng phương tiện, thiết bị kỹ thuật nghiệp vụ và quy trình thu nhập, sử dụng dữ liệu thu được từ phương tiện, thiết bị kỹ thuật do cá nhân, tổ chức cung cấp để phát hiện vi phạm hành chính",
    number: "Số 61/2026/NĐ-CP",
    date: "13/02/2026",
    effectiveDate: "01/04/2026",
    status: "Còn hiệu lực",
    issuer: "Chính phủ",
    desc: "Nghị định quy định danh mục, việc quản lý, sử dụng phương tiện, thiết bị kỹ thuật nghiệp vụ và quy trình thu thập, sử dụng dữ liệu do cá nhân, tổ chức cung cấp để phát hiện vi phạm hành chính. Văn bản chuẩn hóa điều kiện pháp lý của hệ thống camera giám sát giao thông (phạt nguội), máy đo nồng độ cồn, thiết bị cân tải trọng và quy định thời hạn gửi thông báo vi phạm đến chủ xe qua ứng dụng VNeID. Đồng thời, nghị định mở ra cơ chế khuyến khích và bảo vệ người dân cung cấp hình ảnh, video clip quay được về các hành vi vi phạm giao thông cho cơ quan Công an làm căn cứ xác minh xử phạt. Nghị định được ban hành ngày 13/02/2026 và chính thức có hiệu lực thi hành từ ngày 01/04/2026, thay thế Nghị định 135/2021/NĐ-CP.",
    sourceUrl: "https://congbao.chinhphu.vn/van-ban/nghi-dinh-so-61-2026-nd-cp-468978.htm",
    isConsolidated: false,
    sampleAiPrompts: [
      "Quy trình phạt nguội và thời hạn gửi thông báo vi phạm về nhà là bao lâu?",
      "Chưa nộp phạt nguội có được đăng kiểm xe ô tô không?"
    ]
  },
  {
    id: "doc-12",
    category: "nghi-dinh",
    typeLabel: "Nghị định",
    title: "Nghị định xử phạt vi phạm hành chính trong lĩnh vực an ninh, trật tự, an toàn xã hội",
    number: "Số 282/2025/NĐ-CP",
    date: "30/10/2025",
    effectiveDate: "15/12/2025",
    status: "Còn hiệu lực",
    issuer: "Chính phủ",
    desc: "Nghị định quy định xử phạt vi phạm hành chính trong lĩnh vực an ninh trật tự, an toàn xã hội, phòng chống tệ nạn xã hội và bảo vệ hoạt động công vụ. Trong bối cảnh giao thông, văn bản quy định chế tài xử phạt rất nặng đối với các hành vi cản trở, lăng mạ hoặc dùng vũ lực chống đối lực lượng Cảnh sát giao thông đang làm nhiệm vụ kiểm tra, xử lý vi phạm. Các hành vi tụ tập đua xe trái phép, lạng lách đánh võng, cổ vũ đua xe, quay video kích động chống người thi hành công vụ đều bị áp dụng mức phạt tiền kịch khung và tịch thu phương tiện. Nghị định có hiệu lực thi hành từ ngày 15/12/2025, thay thế các quy định xử phạt tương ứng của Nghị định 144/2021/NĐ-CP.",
    sourceUrl: "https://congbao.chinhphu.vn/van-ban/nghi-dinh-so-282-2025-nd-cp-46543/59667.htm",
    isConsolidated: false,
    sampleAiPrompts: [
      "Hành vi chống đối CSGT kiểm tra nồng độ cồn bị phạt tiền bao nhiêu?"
    ]
  },
  {
    id: "doc-13",
    category: "nghi-dinh",
    typeLabel: "Nghị định",
    title: "Nghị định xử phạt vi phạm hành chính trong hoạt động đường bộ",
    number: "Số 336/2025/NĐ-CP",
    date: "22/12/2025",
    effectiveDate: "01/03/2026",
    status: "Còn hiệu lực",
    issuer: "Chính phủ",
    desc: "Nghị định quy định chi tiết về hành vi vi phạm, mức phạt tiền và biện pháp khắc phục hậu quả trong việc bảo vệ kết cấu hạ tầng, xây dựng và khai thác công trình đường bộ. Văn bản tập trung xử lý nghiêm các hành vi thi công công trình đường bộ không phép, không bố trí biển báo cảnh báo ban đêm, xe chở quá tải trọng, quá khổ giới hạn làm hư hại cầu cống, đường sá. Trách nhiệm liên đới được quy định rõ ràng cho cả lái xe, chủ xe cá nhân và doanh nghiệp vận tải khi cố tình bốc xếp, vận chuyển hàng hóa vượt tải trọng cho phép. Nghị định được Chính phủ ban hành ngày 22/12/2025 và có hiệu lực thi hành từ ngày 01/03/2026, thi hành đồng bộ với Luật Đường bộ 2024.",
    sourceUrl: "https://congbao.chinhphu.vn/van-ban/nghi-dinh-so-336-2025-nd-cp-467811/60657.htm",
    isConsolidated: false,
    sampleAiPrompts: [
      "Mức phạt quá tải trọng xe ô tô tải đối với lái xe và chủ xe như thế nào?"
    ]
  },
  {
    id: "doc-14",
    category: "nghi-dinh",
    typeLabel: "Nghị định",
    title: "Nghị định xử phạt vi phạm hành chính trong lĩnh vực giao thông đường sắt",
    number: "Số 81/2026/NĐ-CP",
    date: "19/03/2026",
    effectiveDate: "15/05/2026",
    status: "Còn hiệu lực",
    issuer: "Chính phủ",
    desc: "Nghị định quy định xử phạt các hành vi vi phạm hành chính trong quản lý hạ tầng, bảo vệ hành lang an toàn và quy tắc giao thông đường sắt. Chế tài xử phạt nghiêm minh được áp dụng đối với người điều khiển phương tiện đường bộ không chấp hành tín hiệu đèn, biển báo hoặc cố tình vượt rào chắn khi cần chắn đường sắt đang đóng. Hành vi dừng, đỗ xe trong phạm vi an toàn đường sắt hoặc để rơi vãi vật liệu gây cản trở hành trình của tàu hỏa có thể bị xử phạt tiền hàng chục triệu đồng và tước quyền sử dụng GPLX. Nghị định có hiệu lực thi hành từ ngày 15/05/2026, thay thế Nghị định số 56/2018/NĐ-CP trước đây.",
    sourceUrl: "https://congbao.chinhphu.vn/van-ban/nghi-dinh-so-81-2026-nd-cp-469163/63642.htm",
    isConsolidated: false,
    sampleAiPrompts: [
      "Cố tình vượt rào chắn đường sắt khi chuông đã reo bị phạt bao nhiêu tiền?"
    ]
  },
  {
    id: "doc-15",
    category: "nghi-dinh",
    typeLabel: "Nghị định",
    title: "Nghị định quy định về hoạt động vận tải đường bộ",
    number: "Số 58/2026/VBHN-BXD",
    date: "18/12/2024",
    effectiveDate: "01/01/2025",
    status: "Còn hiệu lực",
    issuer: "Chính phủ / Bộ Xây dựng",
    desc: "Nghị định quy định chi tiết về điều kiện kinh doanh vận tải hành khách và hàng hóa bằng xe ô tô, cùng các tiêu chuẩn quản lý kỹ thuật phương tiện đường bộ. Văn bản bắt buộc tất cả các phương tiện kinh doanh vận tải phải lắp đặt thiết bị giám sát hành trình (GPS) và camera ghi hình người lái xe trên cabin truyền dữ liệu trực tiếp về Cục Đường bộ Việt Nam. Quy định thời gian lái xe an toàn (không quá 4 giờ liên tục và không quá 10 giờ/ngày) cùng quy trình cấp phù hiệu xe hợp đồng, xe buýt và taxi được chuẩn hóa điện tử toàn diện. Bản hợp nhất cập nhật các quy định sửa đổi năm 2026, có hiệu lực áp dụng thống nhất từ ngày 01/01/2025.",
    sourceUrl: "https://congbao.chinhphu.vn/van-ban/van-ban-hop-nhat-so-58-vbhn-bxd-470058/66656.htm",
    isConsolidated: true,
    sampleAiPrompts: [
      "Quy định về thời gian lái xe tối đa trong ngày của tài xế xe khách theo Nghị định vận tải?"
    ],
    relatedDocs: [
      {
        relationType: "goc",
        title: "Nghị định quy định về hoạt động vận tải đường bộ",
        number: "Số 158/2024/NĐ-CP",
        sourceUrl: "https://congbao.chinhphu.vn/van-ban/nghi-dinh-so-158-2024-nd-cp-43540.htm"
      },
      {
        relationType: "sua_doi",
        title: "Nghị định sửa đổi, bổ sung một số điều của Nghị định số 158/2024/NĐ-CP",
        number: "Số 218/2026/NĐ-CP",
        sourceUrl: "https://congbao.chinhphu.vn/van-ban/nghi-dinh-so-218-2026-nd-cp-469823.htm"
      }
    ]
  },
  {
    id: "doc-16",
    category: "thong-tu",
    typeLabel: "Thông tư",
    title: "Thông tư quy định công tác tuần tra, kiểm soát, xử lý vi phạm về TTATGT đường bộ của CSGT",
    number: "Số 19/VBHN-BCA",
    date: "15/11/2024",
    effectiveDate: "01/01/2025",
    status: "Còn hiệu lực",
    issuer: "Bộ Công an",
    desc: "Thông tư quy định về thẩm quyền, trang phục, trang bị phương tiện, vũ khí, công cụ hỗ trợ và quy trình tuần tra, kiểm soát, xử lý vi phạm trật tự an toàn giao thông đường bộ của CSGT. Văn bản quy định rõ 4 trường hợp CSGT được quyền dừng phương tiện để kiểm soát, bao gồm: trực tiếp phát hiện vi phạm, thực hiện theo kế hoạch/chuyên đề đã phê duyệt, có văn bản đề nghị của cơ quan điều tra và nhận tin báo tố giác tội phạm. Quy trình kiểm tra nồng độ cồn, ma túy, kiểm tra giấy tờ tích hợp trên ứng dụng VNeID và văn hóa ứng xử chuẩn mực khi tiếp xúc với nhân dân được luật hóa chặt chẽ. Thông tư có hiệu lực thi hành từ ngày 01/01/2025, thay thế Thông tư 32/2023/TT-BCA trước đây.",
    sourceUrl: "https://luatvietnam.vn/giao-thong/van-ban-hop-nhat-19-vbhn-bca-405783-d5.html",
    isConsolidated: true,
    relatedDocs: [
      {
        relationType: "goc",
        title: "Quy định công tác tuần tra, kiểm soát, xử lý vi phạm pháp luật về TTATGT đường bộ của Cảnh sát giao thông",
        number: "Số 73/2024/TT-BCA",
        sourceUrl: "https://congbao.chinhphu.vn/van-ban/thong-tu-so-73-2024-tt-bca-43336/53041.htm",
      },
      {
        relationType: "sua_doi",
        title: "Thông tư 13/2025/TT-BCA sửa đổi, bổ sung Thông tư 73/2024/TT-BCA",
        number: "Số 13/2025/TT-BCA",
        sourceUrl: "https://congbao.chinhphu.vn/van-ban/thong-tu-so-13-2025-tt-bca-44372/55293.htm",
      },
    ],
    sampleAiPrompts: [
      "4 trường hợp CSGT được quyền dừng xe theo Thông tư 73/2024/TT-BCA?",
      "CSGT có được kiểm tra giấy tờ xe qua tài khoản VNeID không?",
      "Người dân có quyền yêu cầu CSGT xuất trình chuyên đề tuần tra không?"
    ],
    },
  {
    id: "doc-17",
    category: "thong-tu",
    typeLabel: "Thông tư",
    title: "Thông tư quy định về cấp, thu hồi đăng ký xe, biển số định danh",
    number: "Số 41/VBHN-BCA",
    date: "15/11/2024",
    effectiveDate: "01/01/2025",
    status: "Còn hiệu lực",
    issuer: "Bộ Công an",
    desc: "Thông tư quy định về quy trình, thủ tục cấp, thu hồi giấy chứng nhận đăng ký xe và biển số xe cơ giới, xe máy chuyên dùng trên phạm vi cả nước. Điểm then chốt là cơ chế quản lý biển số định danh theo mã định danh cá nhân của chủ xe, cho phép người dân giữ lại biển số khi bán xe để đăng ký cho phương tiện mới. Văn bản đẩy mạnh dịch vụ công trực tuyến toàn trình, cho phép đăng ký xe lần đầu, đổi biển số và chuyển nhượng phương tiện trực tiếp qua Cổng dịch vụ công Bộ Công an hoặc VNeID. Thông tư có hiệu lực thi hành từ ngày 01/01/2025, thay thế Thông tư 24/2023/TT-BCA của Bộ Công an.",
    sourceUrl: "https://vanban.bocongan.gov.vn/co-so-du-lieu-van-ban/van-ban-hop-nhat-thong-tu-quy-dinh-ve-cap-thu-hoi-chung-nhan-dang-ky-xe-bien-so-xe-co-gioi-xe-may-chuyen-dung-1762763470",
    isConsolidated: true,
    sampleAiPrompts: [
      "Bán xe máy/ô tô có được giữ lại biển số định danh không?",
      "Thủ tục thu hồi biển số định danh và đăng ký xe làm thế nào?"
    ],
    relatedDocs: [
      {
        relationType: "goc",
        title: "Thông tư quy định về cấp, thu hồi đăng ký xe, biển số xe cơ giới",
        number: "Số 79/2024/TT-BCA",
        sourceUrl: "https://congbao.chinhphu.vn/van-ban/thong-tu-so-79-2024-tt-bca-43337.htm"
      },
      {
        relationType: "sua_doi",
        title: "Thông tư sửa đổi, bổ sung một số điều của Thông tư số 79/2024/TT-BCA",
        number: "Số 13/2025/TT-BCA",
        sourceUrl: "https://congbao.chinhphu.vn/van-ban/thong-tu-so-13-2025-tt-bca-44372/55293.htm"
      },
      {
        relationType: "sua_doi",
        title: "Thông tư sửa đổi, bổ sung danh mục biểu mẫu đăng ký xe ban hành kèm Thông tư 79/2024/TT-BCA",
        number: "Số 51/2025/TT-BCA",
        sourceUrl: "https://congbao.chinhphu.vn/van-ban/thong-tu-so-51-2025-tt-bca-45356.htm"
      }
    ]
  },
  {
    id: "doc-18",
    category: "thong-tu",
    typeLabel: "Thông tư",
    title: "Thông tư quy định về sát hạch, cấp giấy phép lái xe; cấp, sử dụng GPLX quốc tế",
    number: "Số 108/2026/TT-BCA",
    date: "29/06/2026",
    effectiveDate: "01/07/2026",
    status: "Còn hiệu lực",
    issuer: "Bộ Công an",
    desc: "Thông tư quy định về công tác đào tạo, sát hạch, cấp, đổi giấy phép lái xe cơ giới đường bộ và thủ tục cấp, sử dụng giấy phép lái xe quốc tế do Bộ Công an quản lý. Văn bản nâng cao tiêu chuẩn bài sát hạch lái xe với việc tích hợp phần mềm mô phỏng các tình huống giao thông nguy hiểm và thiết bị chấm điểm tự động gắn trên xe sát hạch. Quy định chi tiết các hạng GPLX mới (A1, A, B1, B, C1, C...) theo chuẩn Công ước Viên, cơ chế kiểm tra lại kiến thức đối với tài xế bị trừ sạch 12 điểm và thủ tục đổi bằng lái trực tuyến. Thông tư có hiệu lực thi hành từ ngày 01/07/2026, đánh dấu việc chuyển giao toàn diện công tác sát hạch cấp GPLX sang lực lượng Công an nhân dân.",
    sourceUrl: "https://congbao.chinhphu.vn/van-ban/thong-tu-so-108-2026-tt-bca-470055.htm",
    sampleAiPrompts: [
      "Thủ tục cấp đổi bằng lái xe ô tô, xe máy do Bộ Công an quản lý như thế nào?"
    ]
  },
  {
    id: "doc-19",
    category: "thong-tu",
    typeLabel: "Thông tư",
    title: "Thông tư quy định về tốc độ và khoảng cách an toàn của xe cơ giới, xe máy chuyên dùng tham gia giao thông",
    number: "Số 38/2024/TT-BGTVT",
    date: "15/11/2024",
    effectiveDate: "01/01/2025",
    status: "Còn hiệu lực",
    issuer: "Bộ Giao thông Vận tải",
    desc: "Thông tư quy định tốc độ tối đa cho phép và khoảng cách an toàn tối thiểu giữa hai xe đối với xe cơ giới, xe máy chuyên dùng tham gia giao thông trên đường bộ. Trong khu vực đông dân cư, tốc độ tối đa là 60 km/h đối với đường đôi hoặc đường một chiều có từ hai làn xe cơ giới trở lên; 50 km/h đối với đường hai chiều hoặc đường một chiều có một làn xe cơ giới. Ngoài khu vực đông dân cư, tốc độ cho phép dao động từ 60 đến 90 km/h tùy loại phương tiện và kết cấu mặt đường; đồng thời quy định cự ly khoảng cách tối thiểu khi chạy tốc độ cao trên cao tốc. Thông tư có hiệu lực thi hành từ ngày 01/01/2025, thay thế Thông tư 31/2019/TT-BGTVT của Bộ Giao thông vận tải.",
    sourceUrl: "https://congbao.chinhphu.vn/van-ban/thong-tu-so-38-2024-tt-bgtvt-43378.htm",
    isConsolidated: false,
    sampleAiPrompts: [
      "Tốc độ tối đa của xe máy trong khu vực đông dân cư là bao nhiêu km/h?",
      "Quy định khoảng cách an toàn tối thiểu giữa 2 xe khi chạy 80km/h?"
    ]
  },
  {
    id: "doc-20",
    category: "quy-chuan",
    typeLabel: "Quy chuẩn",
    title: "Quy chuẩn kỹ thuật quốc gia về báo hiệu đường bộ",
    number: "Thông tư 51/2024/TT-BGTVT",
    date: "15/11/2024",
    effectiveDate: "01/01/2025",
    status: "Còn hiệu lực",
    issuer: "Bộ Giao thông Vận tải",
    desc: "Thông tư ban hành Quy chuẩn kỹ thuật quốc gia QCVN 41:2024/BGTVT quy định bắt buộc về hình dáng, kích thước, màu sắc, vị trí lắp đặt và ý nghĩa hiệu lực của hệ thống báo hiệu đường bộ. Quy chuẩn làm rõ thứ tự ưu tiên hiệu lực: hiệu lệnh của người điều khiển giao thông có giá trị cao nhất, tiếp theo là tín hiệu đèn, biển báo hiệu và vạch sơn kẻ đường. Văn bản chuẩn hóa ý nghĩa các biển cấm vượt, biển giới hạn tốc độ, vạch liền, vạch đứt và quy chuẩn đèn tín hiệu giao thông (bao gồm đèn vàng và đèn mũi tên rẽ). Quy chuẩn có hiệu lực thi hành từ ngày 01/01/2025, thay thế toàn diện QCVN 41:2019/BGTVT trước đây.",
    sourceUrl: "https://congbao.chinhphu.vn/van-ban/thong-tu-so-51-2024-tt-bgtvt-43387/53152.htm",
    isConsolidated: false,
    sampleAiPrompts: [
      "Thứ tự ưu tiên giữa hiệu lệnh CSGT, đèn giao thông và biển báo theo QCVN 41?",
      "Đè vạch sơn kẻ đường nào thì bị xử phạt vi phạm?"
    ]
  },
  {
    id: "doc-21",
    category: "thong-tu",
    typeLabel: "Thông tư",
    title: "Thông tư quy định quy trình điều tra, giải quyết tai nạn giao thông đường bộ của cảnh sát giao thông",
    number: "Số 18/VBHN-BCA",
    date: "13/11/2024",
    effectiveDate: "01/01/2025",
    status: "Còn hiệu lực",
    issuer: "Bộ Công an",
    desc: "Thông tư quy định về quy trình tiếp nhận tin báo, bảo vệ hiện trường, khám nghiệm, điều tra và giải quyết các vụ tai nạn giao thông đường bộ của lực lượng Cảnh sát giao thông. Văn bản phân định ranh giới xử lý: các vụ tai nạn có dấu hiệu tội phạm (chết người, thương tật từ 61% trở lên hoặc thiệt hại tài sản lớn) phải bàn giao ngay cho Cơ quan Cảnh sát điều tra thụ lý. Quy định rõ thời hạn tạm giữ phương tiện để phục vụ khám nghiệm kỹ thuật, quy trình thu thập dấu vết phanh, trích xuất camera hành trình và thủ tục hòa giải, giải quyết bồi thường dân sự. Thông tư có hiệu lực thi hành từ ngày 01/01/2025, thay thế Thông tư 63/2020/TT-BCA của Bộ Công an.",
    sourceUrl: "https://luatvietnam.vn/giao-thong/van-ban-hop-nhat-18-vbhn-bca-nam-2025-do-bo-cong-an-ban-hanh-hop-nhat-thong-tu-quy-dinh-quy-trinh-dieu-tra-giai-quyet-tai-nan-giao-thong-duong-bo-cua-canh-sat-giao-thong-405781-d5.html",
    isConsolidated: true,
    sampleAiPrompts: [
      "Khi xảy ra tai nạn giao thông người lái xe cần thực hiện ngay những bước nào theo quy định?",
      "CSGT được tạm giữ xe trong bao lâu để điều tra giải quyết tai nạn?"
    ],
    relatedDocs: [
      {
        relationType: "goc",
        title: "Thông tư quy định quy trình điều tra, giải quyết tai nạn giao thông đường bộ của Cảnh sát giao thông",
        number: "Số 72/2024/TT-BCA",
        sourceUrl: "https://congbao.chinhphu.vn/van-ban/thong-tu-so-72-2024-tt-bca-43281/52935.htm"
      },
      {
        relationType: "sua_doi",
        title: "Thông tư sửa đổi, bổ sung một số điều của các thông tư quy định về trật tự, an toàn giao thông đường bộ, đường sắt và đường thủy nội địa",
        number: "Số 13/2025/TT-BCA",
        sourceUrl: "https://congbao.chinhphu.vn/van-ban/thong-tu-so-13-2025-tt-bca-44372/55293.htm"
      }
    ]
  },
  {
    id: "doc-22",
    category: "thong-tu",
    typeLabel: "Thông tư",
    title: "Thông tư quy định thực hiện dân chủ trong công tác bảo đảm trật tự, an toàn giao thông",
    number: "Số 21/VBHN-BCA",
    date: "28/11/2019",
    effectiveDate: "15/11/2024",
    status: "Còn hiệu lực",
    issuer: "Bộ Công an",
    desc: "Thông tư quy định về mục đích, nguyên tắc, nội dung và hình thức thực hiện dân chủ trong công tác tuần tra, kiểm soát, xử lý vi phạm trật tự an toàn giao thông của lực lượng Công an nhân dân. Văn bản quy định rõ các nội dung CSGT bắt buộc phải công khai minh bạch như kế hoạch tuần tra, tên cán bộ chiến sĩ làm nhiệm vụ, tuyến đường kiểm soát và số điện thoại đường dây nóng. Công dân có quyền giám sát hoạt động của CSGT bằng mắt hoặc thông qua thiết bị ghi âm, ghi hình nhưng phải bảo đảm trật tự, đứng ngoài khu vực cọc tiêu rào chắn bảo vệ hiện trường và không được cản trở cán bộ làm nhiệm vụ. Bản hợp nhất cập nhật các sửa đổi của Thông tư 46/2024/TT-BCA, có hiệu lực áp dụng thống nhất từ ngày 15/11/2024.",
    sourceUrl: "https://hethongphapluat.com/van-ban-hop-nhat-21-vbhn-bca-nam-2024-hop-nhat-thong-tu-quy-dinh-ve-thuc-hien-dan-chu-trong-cong-tac-bao-dam-trat-tu-an-toan-giao-thong-do-bo-truong-bo-cong-an-ban-hanh.html",
    isConsolidated: true,
    sampleAiPrompts: [
      "Người dân có được quay phim, ghi âm khi làm việc với Cảnh sát giao thông không?",
      "Những điều kiện người dân cần tuân thủ khi giám sát CSGT làm nhiệm vụ?"
    ],
    relatedDocs: [
      {
        relationType: "goc",
        title: "Thông tư ban hành quy định thực hiện dân chủ trong công tác bảo đảm trật tự, an toàn giao thông",
        number: "Số 67/2019/TT-BCA",
        sourceUrl: "https://congan.lamdong.gov.vn/UpLoaded/Files/thong-tu/bca/TT-67.2019.pdf"
      },
      {
        relationType: "sua_doi",
        title: "Thông tư sửa đổi, bổ sung một số điều của Thông tư số 67/2019/TT-BCA",
        number: "Số 46/2024/TT-BCA",
        sourceUrl: "https://datafiles.chinhphu.vn/cpp/files/vbpq/2024/9/46-bca.signed.pdf"
      }
    ]
  }
];
