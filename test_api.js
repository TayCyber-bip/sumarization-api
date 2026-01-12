// API Test Script for Node.js / Mobile App
// Chạy: node test_api.js

const baseURL = 'http://localhost:8000';

async function testAPI() {
  console.log('=== API Test Script ===');
  console.log(`Base URL: ${baseURL}\n`);

  try {
    // 1. Health Check
    console.log('1. Health Check...');
    const health = await fetch(`${baseURL}/health`).then(r => r.json());
    console.log('✅ Status:', health.status);
    console.log('✅ Services:', health.services.join(', '));
    console.log('');

    // 2. Tạo session mới - Chat lần đầu
    console.log('2. Creating new chat session...');
    const chat1 = await fetch(`${baseURL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: 'I have a headache and fever' })
    }).then(r => r.json());

    const sessionId = chat1.session_id;
    console.log('✅ Session ID:', sessionId);
    console.log('✅ User:', chat1.message);
    console.log('✅ Assistant:', chat1.response);
    console.log('');

    // 3. Chat tiếp với session_id
    console.log('3. Continuing chat with session ID...');
    const chat2 = await fetch(`${baseURL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: 'What should I do?',
        session_id: sessionId
      })
    }).then(r => r.json());

    console.log('✅ User:', chat2.message);
    console.log('✅ Assistant:', chat2.response);
    console.log('');

    // 4. Lấy chat history
    console.log('4. Getting chat history...');
    const history = await fetch(`${baseURL}/chat/history/${sessionId}?limit=50`).then(r => r.json());
    console.log('✅ Session ID:', history.session_id);
    console.log('✅ Message count:', history.count);
    console.log('✅ Messages:');
    history.messages.forEach((msg, i) => {
      console.log(`  [${i + 1}] User: ${msg.user}`);
      console.log(`      Assistant: ${msg.assistant}`);
    });
    console.log('');

    // 5. List sessions
    console.log('5. Listing all sessions...');
    const sessions = await fetch(`${baseURL}/chat/sessions?limit=10`).then(r => r.json());
    console.log('✅ Total sessions:', sessions.count);
    sessions.sessions.forEach(session => {
      console.log(`  Session: ${session.session_id}`);
      console.log(`    Last message: ${session.last_message_at}`);
      console.log(`    Message count: ${session.message_count}`);
    });
    console.log('');

    // 6. Test Summarization
    console.log('6. Testing summarization...');
    const summary = await fetch(`${baseURL}/summarize`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        text: 'Influenza, commonly known as the flu, is an infectious disease caused by influenza viruses. Symptoms range from mild to severe and often include fever, runny nose, sore throat, muscle pain, headache, coughing, and fatigue.'
      })
    }).then(r => r.json());
    console.log('✅ Summary:', summary.summary);
    console.log('');

    console.log('=== Test Complete ===');

  } catch (error) {
    console.error('❌ Error:', error.message);
    process.exit(1);
  }
}

// Chạy test
testAPI();

