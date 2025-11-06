<?php
// api.php - Gateway to AI server

// Luôn đảm bảo phản hồi là định dạng JSON
header('Content-Type: application/json');

// Tải tệp AI client
require_once 'ai-chat-client.php';

// 1. Đọc dữ liệu JSON thô từ yêu cầu
$json_data = file_get_contents('php://input');
if (!$json_data) {
    http_response_code(400); // Bad Request
    echo json_encode(['response' => 'Lỗi: Không nhận được dữ liệu.']);
    exit;
}

// 2. Giải mã dữ liệu JSON
$request_data = json_decode($json_data, true);
if (json_last_error() !== JSON_ERROR_NONE) {
    http_response_code(400); // Bad Request
    echo json_encode(['response' => 'Lỗi: Dữ liệu gửi lên không đúng định dạng JSON.']);
    exit;
}

// 3. Lấy câu hỏi của người dùng từ khóa 'message'
$user_question = $request_data['message'] ?? '';
if (empty($user_question)) {
    http_response_code(400); // Bad Request
    echo json_encode(['response' => 'Lỗi: Nội dung câu hỏi không được để trống.']);
    exit;
}

// 4. Sử dụng đúng lớp AI Client và xử lý
try {
    // Sử dụng lớp 'StoreAIClient' đã được định nghĩa
    $aiClient = new StoreAIClient(); 
    
    // Gọi phương thức askAI
    $ai_result = $aiClient->askAI($user_question);

    // Chuẩn bị phản hồi theo định dạng mà JavaScript mong đợi
    if ($ai_result['success']) {
        $response_payload = ['response' => $ai_result['answer']];
    } else {
        // Nếu client AI trả về lỗi, chuyển tiếp thông báo lỗi đó
        $response_payload = ['response' => $ai_result['answer'] ?? 'Xin lỗi, có lỗi xảy ra từ phía AI.'];
    }
    
    echo json_encode($response_payload, JSON_UNESCAPED_UNICODE);

} catch (Exception $e) {
    http_response_code(500); // Internal Server Error
    // Ghi lại lỗi để debug, không hiển thị cho người dùng
    error_log('Lỗi trong api.php: ' . $e->getMessage());
    echo json_encode(['response' => 'Xin lỗi, máy chủ đang gặp lỗi nội bộ.']);
}

?>