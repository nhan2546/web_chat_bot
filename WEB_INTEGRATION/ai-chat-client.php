<?php
// ai-chat-client.php
// Client kết nối đến AI Server Python của bạn

class StoreAIClient {
    private $apiUrl;
    private $timeout;
    
    public function __construct($serverUrl = null, $timeout = 30) {
        // Kết nối đến app.py của bạn
        $this->apiUrl = $serverUrl ?: 'http://localhost:5000/api/chat';
        $this->timeout = $timeout;
    }
    
    /**
     * Gửi câu hỏi đến AI server và nhận response
     */
    public function askAI($question, $userContext = []) {
        if (empty(trim($question))) {
            return [
                'success' => false,
                'answer' => 'Câu hỏi không được để trống.',
                'error' => 'empty_question'
            ];
        }
        
        // Chuẩn bị payload theo format app.py của bạn
        $payload = [
            'question' => trim($question)
            // app.py của bạn chỉ cần 'question', không cần context
        ];
        
        return $this->makeApiRequest($payload);
    }
    
    /**
     * Thực hiện API request đến AI server
     */
    private function makeApiRequest($payload) {
        $jsonPayload = json_encode($payload, JSON_UNESCAPED_UNICODE);
        
        if (json_last_error() !== JSON_ERROR_NONE) {
            return [
                'success' => false,
                'answer' => 'Lỗi xử lý dữ liệu.',
                'error' => 'json_encode_error'
            ];
        }
        
        // Sử dụng cURL để gọi API
        $ch = curl_init();
        
        curl_setopt_array($ch, [
            CURLOPT_URL => $this->apiUrl,
            CURLOPT_POST => true,
            CURLOPT_POSTFIELDS => $jsonPayload,
            CURLOPT_HTTPHEADER => [
                'Content-Type: application/json',
                'Content-Length: ' . strlen($jsonPayload),
                'User-Agent: StoreAI-ChatClient/1.0'
            ],
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT => $this->timeout,
            CURLOPT_CONNECTTIMEOUT => 10,
            CURLOPT_SSL_VERIFYPEER => false, // Tắt SSL verify cho dev
            CURLOPT_FOLLOWLOCATION => true,
        ]);
        
        $startTime = microtime(true);
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        $totalTime = round((microtime(true) - $startTime) * 1000, 2); // ms
        
        $error = curl_error($ch);
        curl_close($ch);
        
        // Xử lý response
        if ($error) {
            error_log("AI Client cURL Error: " . $error);
            return [
                'success' => false,
                'answer' => 'Lỗi kết nối đến AI server. Vui lòng thử lại sau.',
                'error' => 'curl_error',
                'details' => $error,
                'response_time' => $totalTime
            ];
        }
        
        if ($httpCode !== 200) {
            error_log("AI Client HTTP Error: Code " . $httpCode);
            return [
                'success' => false,
                'answer' => 'AI server đang bận. Vui lòng thử lại sau.',
                'error' => 'http_error',
                'http_code' => $httpCode,
                'response_time' => $totalTime
            ];
        }
        
        // Parse JSON response
        $data = json_decode($response, true);
        
        if (json_last_error() !== JSON_ERROR_NONE) {
            error_log("AI Client JSON Error: " . json_last_error_msg());
            return [
                'success' => false,
                'answer' => 'Lỗi xử lý phản hồi từ AI.',
                'error' => 'json_decode_error',
                'raw_response' => substr($response, 0, 200),
                'response_time' => $totalTime
            ];
        }
        
        // Kiểm tra cấu trúc response theo app.py của bạn
        if (isset($data['success']) && $data['success'] === true) {
            return [
                'success' => true,
                'answer' => $data['answer'] ?? 'Không có nội dung phản hồi.',
                'question' => $data['question'] ?? '',
                'context' => $data['context'] ?? [],
                'response_data' => $data,
                'response_time' => $totalTime
            ];
        } else {
            // Xử lý error response từ app.py
            $errorMessage = $data['error'] ?? 'AI chưa thể trả lời câu hỏi này.';
            return [
                'success' => false,
                'answer' => $errorMessage,
                'error' => 'api_error',
                'response_data' => $data,
                'response_time' => $totalTime
            ];
        }
    }
    
    /**
     * Health check - Kiểm tra AI server có hoạt động không
     */
    public function healthCheck() {
        $healthUrl = str_replace('/api/chat', '/api/health', $this->apiUrl);
        
        $ch = curl_init();
        curl_setopt_array($ch, [
            CURLOPT_URL => $healthUrl,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT => 5,
            CURLOPT_SSL_VERIFYPEER => false
        ]);
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        if ($httpCode === 200) {
            $data = json_decode($response, true);
            return [
                'status' => 'healthy',
                'service' => $data['service'] ?? 'unknown',
                'timestamp' => $data['timestamp'] ?? null
            ];
        }
        
        return [
            'status' => 'unhealthy',
            'http_code' => $httpCode
        ];
    }
    
    /**
     * Lấy thông tin cửa hàng từ AI server (debug)
     */
    public function getStoreInfo() {
        $storeInfoUrl = str_replace('/api/chat', '/api/store-info', $this->apiUrl);
        
        $ch = curl_init();
        curl_setopt_array($ch, [
            CURLOPT_URL => $storeInfoUrl,
            CURLOPT_RETURNTRANSFER => true,
            CURLOPT_TIMEOUT => 10
        ]);
        
        $response = curl_exec($ch);
        $httpCode = curl_getinfo($ch, CURLINFO_HTTP_CODE);
        curl_close($ch);
        
        if ($httpCode === 200) {
            return json_decode($response, true);
        }
        
        return null;
    }
}

/**
 * Hàm helper để sử dụng nhanh
 */
function get_ai_response($question) {
    static $aiClient = null;
    
    if ($aiClient === null) {
        $aiClient = new StoreAIClient();
    }
    
    return $aiClient->askAI($question);
}

/**
 * Health check nhanh
 */
function check_ai_server_health() {
    $aiClient = new StoreAIClient();
    return $aiClient->healthCheck();
}

// Demo sử dụng (có thể xóa sau)
if (php_sapi_name() === 'cli' && isset($argv[1]) && $argv[1] === 'test') {
    echo "=== Testing AI Chat Client ===\n";
    
    $aiClient = new StoreAIClient();
    
    // Test health check
    echo "1. Health Check: ";
    $health = $aiClient->healthCheck();
    print_r($health);
    
    // Test store info
    echo "2. Store Info: ";
    $storeInfo = $aiClient->getStoreInfo();
    if ($storeInfo) {
        echo "OK - " . ($storeInfo['store_context']['total_products'] ?? 0) . " products\n";
    } else {
        echo "Failed\n";
    }
    
    // Test câu hỏi
    echo "3. Test Question: ";
    $response = $aiClient->askAI("Xin chào, bạn có những sản phẩm gì?");
    if ($response['success']) {
        echo "SUCCESS: " . substr($response['answer'], 0, 100) . "...\n";
    } else {
        echo "FAILED: " . $response['answer'] . "\n";
    }
    
    echo "4. Response Time: " . ($response['response_time'] ?? 'N/A') . "ms\n";
}
?>