<?php
// test_php.php
require_once 'ai-chat-client.php';

echo "<h1>🧪 TEST PHP AI CLIENT</h1>";

$client = new FullAutoAIClient();

// Test health
echo "<h2>Health Check</h2>";
$health = $client->healthCheck();
echo "<pre>";
print_r($health);
echo "</pre>";

// Test questions
echo "<h2>Chat Tests</h2>";
$questions = [
    "Hello",
    "Xin chao", 
    "iPhone",
    "Laptop"
];

foreach ($questions as $question) {
    echo "<div style='border: 1px solid #ccc; margin: 10px; padding: 15px;'>";
    echo "<h3>Q: " . htmlspecialchars($question) . "</h3>";
    
    $response = $client->askAI($question);
    
    echo "<pre>";
    print_r($response);
    echo "</pre>";
    
    echo "</div>";
}
?>