/**
 * SGROUP CRM - GOOGLE APPS SCRIPT FOR ODOO 19 SYNC
 * 
 * Instructions:
 * 1. Open Google Sheets.
 * 2. Click "Extensions" > "Apps Script".
 * 3. Clear any existing code and paste this script.
 * 4. Update ODOO_URL to your active ngrok URL.
 * 5. Save the project and click "Run" -> "setupTrigger" once.
 */

// --- CẤU HÌNH KẾT NỐI ODOO ---
const ODOO_URL = 'https://buckskin-foil-procedure.ngrok-free.dev'; // URL ngrok của bạn
const DB_NAME = 'odoo_db';
const USERNAME = 'SgroupCRM';
const PASSWORD = 'HoangPhuc';

/**
 * Tự động chạy mỗi khi có Form gửi dữ liệu mới về Sheets
 */
function onFormSubmitTrigger(e) {
  if (!e) return;
  const sheet = e.range.getSheet();
  const row = e.range.getRow();

  syncRowToOdoo(sheet, row);
}

/**
 * Tạo Menu nút bấm trên Google Sheets để đồng bộ thủ công dòng được chọn
 */
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('Sgroup CRM')
    .addItem('Đồng bộ dòng đang chọn', 'syncSelectedRows')
    .addItem('Cài đặt tự động kích hoạt (Trigger)', 'setupTrigger')
    .addToUi();
}

/**
 * Hàm thiết lập tự động chạy (Trigger) tự động bằng code
 */
function setupTrigger() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet();

  // Xóa các trigger trùng lặp cũ
  const triggers = ScriptApp.getProjectTriggers();
  for (let i = 0; i < triggers.length; i++) {
    if (triggers[i].getHandlerFunction() === 'onFormSubmitTrigger') {
      ScriptApp.deleteTrigger(triggers[i]);
    }
  }

  // Tạo trigger mới khi gửi Form
  ScriptApp.newTrigger('onFormSubmitTrigger')
    .forSpreadsheet(sheet)
    .onFormSubmit()
    .create();

  safeAlert('Đã thiết lập tự động đồng bộ thời gian thực thành công! Từ giờ khi có khách điền Form, dữ liệu sẽ tự động đẩy sang Odoo.');
}

/**
 * Hàm đồng bộ các dòng đang được bôi đen (Quét chọn) trên Sheet
 */
function syncSelectedRows() {
  const sheet = SpreadsheetApp.getActiveSheet();
  const range = sheet.getActiveRange();
  const startRow = range.getRow();
  const numRows = range.getNumRows();

  // Bỏ qua dòng tiêu đề
  const actualStartRow = startRow === 1 ? 2 : startRow;
  const endRow = startRow + numRows - 1;

  let successCount = 0;
  let skippedCount = 0;
  let errorCount = 0;

  for (let row = actualStartRow; row <= endRow; row++) {
    const statusVal = sheet.getRange(row, 5).getValue(); // Cột E: Trạng thái đồng bộ
    if (statusVal === 'ĐÃ ĐỒNG BỘ') {
      skippedCount++;
      continue;
    }

    const success = syncRowToOdoo(sheet, row);
    if (success) {
      successCount++;
    } else {
      errorCount++;
    }
  }

  safeAlert('Kết quả đồng bộ:\n- Thành công: ' + successCount + ' dòng\n- Bỏ qua (Đã đồng bộ trước đó): ' + skippedCount + ' dòng\n- Lỗi kết nối: ' + errorCount + ' dòng.');
}

/**
 * Lấy dữ liệu của 1 dòng cụ thể và gọi XML-RPC của Odoo để đẩy sang
 */
function syncRowToOdoo(sheet, row) {
  try {
    // 1. Trích xuất thông tin dựa trên cấu trúc cột của bạn
    const name = sheet.getRange(row, 2).getValue().toString().trim(); // Cột B: Tên của Anh/Chị là:
    const phone = sheet.getRange(row, 3).getValue().toString().trim(); // Cột C: Số điện thoại liên hệ
    const project = sheet.getRange(row, 4).getValue().toString().trim(); // Cột D: Dự án quan tâm

    // Nếu thiếu các trường bắt buộc thì bỏ qua
    if (!name || !phone) {
      sheet.getRange(row, 5).setValue('BỎ QUA - THIẾU TÊN/SĐT').setFontColor('#e74c3c').setFontWeight('bold');
      return false;
    }

    sheet.getRange(row, 5).setValue('ĐANG ĐỒNG BỘ...').setFontColor('#f39c12').setFontWeight('bold');
    SpreadsheetApp.flush();

    // 2. Kết nối XML-RPC đến Odoo
    const uid = authenticateOdoo();
    if (!uid) {
      sheet.getRange(row, 5).setValue('LỖI XÁC THỰC ODOO').setFontColor('#e74c3c').setFontWeight('bold');
      return false;
    }

    // Tạo bản ghi Lead (sgroup.ad.data)
    const vals = {
      'name': name,
      'phone': phone,
      'project': project,
      'source': 'Google Form',
      'state': 'draft'
    };

    const recordId = createOdooRecord(uid, 'sgroup.ad.data', vals);
    if (recordId) {
      // Lưu lại trạng thái Đã đồng bộ và ID bản ghi Odoo vào cột E và F
      sheet.getRange(row, 5).setValue('ĐÃ ĐỒNG BỘ').setFontColor('#2ecc71').setFontWeight('bold');
      sheet.getRange(row, 6).setValue(recordId).setHorizontalAlignment('center');
      return true;
    } else {
      sheet.getRange(row, 5).setValue('LỖI ĐẨY DỮ LIỆU').setFontColor('#e74c3c').setFontWeight('bold');
      return false;
    }
  } catch (err) {
    Logger.log('Lỗi đồng bộ dòng ' + row + ': ' + err.toString());
    sheet.getRange(row, 5).setValue('LỖI: ' + err.toString().substring(0, 30)).setFontColor('#e74c3c').setFontWeight('bold');
    return false;
  }
}

// ==========================================
// THƯ VIỆN XML-RPC ENGINE TRÊN GOOGLE APPS SCRIPT
// ==========================================

/**
 * Xác thực thông tin đăng nhập và trả về User ID (UID)
 */
function authenticateOdoo() {
  const url = ODOO_URL + '/xmlrpc/2/common';
  const xmlPayload =
    '<?xml version="1.0"?>' +
    '<methodCall>' +
    '<methodName>authenticate</methodName>' +
    '<params>' +
    '<param><value><string>' + DB_NAME + '</string></value></param>' +
    '<param><value><string>' + USERNAME + '</string></value></param>' +
    '<param><value><string>' + PASSWORD + '</string></value></param>' +
    '<param><value><struct/></value></param>' +
    '</params>' +
    '</methodCall>';

  const options = {
    'method': 'post',
    'contentType': 'text/xml',
    'payload': xmlPayload,
    'muteHttpExceptions': true
  };

  const response = UrlFetchApp.fetch(url, options);
  const responseText = response.getContentText();

  // Trích xuất giá trị int từ phản hồi XML
  const match = responseText.match(/<int>(\d+)<\/int>/);
  if (match && match[1]) {
    return parseInt(match[1], 10);
  }

  Logger.log('Không thể xác thực Odoo. Chi tiết phản hồi: ' + responseText);
  return null;
}

/**
 * Gọi hàm 'create' trên Odoo để lưu dữ liệu
 */
function createOdooRecord(uid, model, vals) {
  const url = ODOO_URL + '/xmlrpc/2/object';

  // Tạo cấu trúc XML cho cấu trúc Dictionary/Struct của Odoo
  let structMembers = '';
  for (let key in vals) {
    structMembers +=
      '<member>' +
      '<name>' + key + '</name>' +
      '<value><string>' + escapeXml(vals[key].toString()) + '</string></value>' +
      '</member>';
  }

  const xmlPayload =
    '<?xml version="1.0"?>' +
    '<methodCall>' +
    '<methodName>execute_kw</methodName>' +
    '<params>' +
    '<param><value><string>' + DB_NAME + '</string></value></param>' +
    '<param><value><int>' + uid + '</int></value></param>' +
    '<param><value><string>' + PASSWORD + '</string></value></param>' +
    '<param><value><string>' + model + '</string></value></param>' +
    '<param><value><string>create</string></value></param>' +
    '<param>' +
    '<value>' +
    '<array>' +
    '<data>' +
    '<value>' +
    '<array>' +
    '<data>' +
    '<value>' +
    '<struct>' +
    structMembers +
    '</struct>' +
    '</value>' +
    '</data>' +
    '</array>' +
    '</value>' +
    '</data>' +
    '</array>' +
    '</value>' +
    '</param>' +
    '</params>' +
    '</methodCall>';

  const options = {
    'method': 'post',
    'contentType': 'text/xml',
    'payload': xmlPayload,
    'muteHttpExceptions': true
  };

  const response = UrlFetchApp.fetch(url, options);
  const responseText = response.getContentText();

  // Odoo create trả về ID số nguyên của bản ghi mới
  // XML phản hồi có dạng: <value><int>ID</int></value> hoặc nằm trong array <array><data><value><int>ID</int></value></data></array>
  const match = responseText.match(/<int>(\d+)<\/int>/);
  if (match && match[1]) {
    return parseInt(match[1], 10);
  }

  Logger.log('Lỗi gọi create trên Odoo. Chi tiết phản hồi: ' + responseText);
  return null;
}

/**
 * Tránh lỗi ký tự XML đặc biệt
 */
function escapeXml(unsafe) {
  return unsafe.replace(/[<>&'"]/g, function (c) {
    switch (c) {
      case '<': return '&lt;';
      case '>': return '&gt;';
      case '&': return '&amp;';
      case '\'': return '&apos;';
      case '"': return '&quot;';
    }
  });
}

/**
 * Hiển thị hộp thoại thông báo an toàn, tránh lỗi chạy trong môi trường Script Editor
 */
function safeAlert(message) {
  try {
    SpreadsheetApp.getUi().alert(message);
  } catch (e) {
    Logger.log('📢 THÔNG BÁO: ' + message);
  }
}
