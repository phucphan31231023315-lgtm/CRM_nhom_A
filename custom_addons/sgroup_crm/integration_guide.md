# HƯỚNG DẪN CÀI ĐẶT ĐỒNG BỘ THỜI GIAN THỰC (GOOGLE FORM -> ODOO 19)

Tài liệu này hướng dẫn bạn cài đặt đoạn mã **Google Apps Script** vào file Google Sheets của bạn để tự động chuyển tiếp khách hàng điền từ Google Form trực tiếp về Odoo 19 qua **ngrok**.

---

## 📋 Yêu cầu chuẩn bị trên Google Sheets

1. Mở file Google Sheets **"Danh sách khách hàng"** của bạn lên.
2. Thêm tiêu đề cho 2 cột tiếp theo trên sheet:
   - **Cột E**: Điền chữ **`Trạng thái đồng bộ`** vào dòng 1.
   - **Cột F**: Điền chữ **`Odoo ID`** vào dòng 1.
   
*(Cột E sẽ hiển thị chữ xanh **ĐÃ ĐỒNG BỘ** khi thành công, cột F sẽ lưu mã số ID khách hàng trên Odoo để tránh trùng lặp dữ liệu)*.

---

## 🛠️ Các bước cài đặt Google Apps Script

### Bước 1: Mở trình soạn thảo mã nguồn
1. Trên thanh menu của Google Sheets, chọn **Tiện ích mở rộng** (Extensions) > **Apps Script**.
2. Một giao diện lập trình web mới sẽ hiện ra. Bạn hãy xóa sạch toàn bộ mã nguồn mặc định (nếu có) trong ô soạn thảo.

### Bước 2: Dán mã nguồn đồng bộ
1. Mở file [GoogleAppsScript.js](file:///d:/Odoo%2019/custom_addons/sgroup_crm/GoogleAppsScript.js) mà tôi vừa tạo trong máy của bạn lên.
2. Copy toàn bộ đoạn mã trong file đó và **Paste (Dán)** vào ô soạn thảo Apps Script trên trình duyệt.
3. Bấm biểu tượng **Save (Lưu)** hình chiếc đĩa mềm ở góc trên.

### Bước 3: Cấu hình URL ngrok
1. Bạn nhìn dòng số 12 của mã nguồn:
   ```javascript
   const ODOO_URL = 'https://buckskin-foil-procedure.ngrok-free.dev';
   ```
   *Lưu ý: Tôi đã điền sẵn URL ngrok hiện tại của bạn là `https://buckskin-foil-procedure.ngrok-free.dev`. Nếu sau này ngrok được tắt đi bật lại và đổi URL mới, bạn chỉ cần mở lại Apps Script này và cập nhật lại dòng số 12 này.*

### Bước 4: Chạy thiết lập tự động (Trigger)
1. Ở phía trên cùng của trình soạn thảo, tại ô chọn hàm, hãy chọn hàm **`setupTrigger`**.
2. Nhấn nút ▶️ **Run** (Chạy) ngay bên cạnh.
3. **Cấp quyền truy cập cho script**:
   - Google sẽ hiển thị một thông báo yêu cầu cấp quyền truy cập tài khoản.
   - Bạn nhấn **Xem quyền** (Review Permissions) > Chọn tài khoản Google của bạn.
   - Chọn **Nâng cao** (Advanced) ở góc dưới bên trái > Chọn **Đi tới dự án không an toàn** (Go to Untitled project (unsafe)).
   - Nhấn **Cho phép** (Allow) để cấp quyền.
4. Khi chạy xong, màn hình sẽ thông báo: *"Đã thiết lập tự động đồng bộ thời gian thực thành công!"*

---

## 🚀 Thao tác và Kiểm tra kết quả

### Cách 1: Test tự động điền Form (Real-time)
1. Bạn hãy mở link Google Form của bạn lên và điền thử một khách hàng mới (Ví dụ: Tên: *Nguyễn Văn Test*, SĐT: *0987654321*, Dự án: *Legacy 66*).
2. Quay lại file Google Sheet, bạn sẽ thấy dòng dữ liệu mới tự động xuất hiện.
3. Sau khoảng 2-3 giây, cột E sẽ chuyển sang trạng thái màu cam **`ĐANG ĐỒNG BỘ...`**, rồi chuyển thành màu xanh **`ĐÃ ĐỒNG BỘ`** và cột F xuất hiện mã số ID (ví dụ: `1`).
4. Vào Odoo `http://localhost:8069` > Menu **Sgroup CRM** > **Dữ liệu quảng cáo (Leads)**. Khách hàng này đã được đồng bộ về và tự động chia cho nhân viên sale theo đúng quy tắc xoay vòng!

### Cách 2: Đồng bộ thủ công các dòng cũ
1. F5 lại trang Google Sheet của bạn. Bạn sẽ thấy trên thanh menu của Sheets xuất hiện một menu mới tên là **`Sgroup CRM`**.
2. Bạn dùng chuột bôi đen (quét chọn) các dòng dữ liệu cũ chưa đồng bộ.
3. Nhấp chọn menu **`Sgroup CRM`** > chọn **`Đồng bộ dòng đang chọn`**.
4. Script sẽ tự động chạy qua từng dòng, đẩy thông tin lên Odoo và báo cáo kết quả tổng hợp bằng hộp thoại pop-up!
