import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { updateField, addChatMessage } from './store';
import axios from 'axios';
import './App.css';

function App() {
  const dispatch = useDispatch();
  const formData = useSelector((state) => state.interaction);
  const [userInput, setUserInput] = useState('');

  const handleChatSubmit = async () => {
    const userMsg = { role: 'user', content: userInput };
    dispatch(addChatMessage(userMsg));

    try {
      const res = await axios.post('http://localhost:8000/chat', { message: userInput });
      console.log("Backend Data Received:", res.data.data);
      if (res.data.data) {
        dispatch(updateField(res.data.data));
      }
      dispatch(addChatMessage({ role: 'assistant', content: res.data.response }));
    } catch (err) {
      console.error("Error communicating with AI agent", err);
    }
    setUserInput('');
  };

  return (
    <div className="container" style={{ fontFamily: 'Inter, sans-serif' }}>
      <header><h2>AI-First CRM: HCP Interaction</h2></header>
      <div className="main-layout">
        {/* LEFT: STRUCTURED FORM */}

        <div className="form-section">
          <h3>Log Interaction</h3>
          <div className="form-group">
            <label>Healthcare Professional Name</label>
            <input
              type="text"
              value={formData.hcp_name || ''}
              onChange={(e) => dispatch(updateField({ hcp_name: e.target.value }))}
              placeholder="HCP Name..."
            />
          </div>
          <div className="form-group">
            <label>Interaction Type</label>
            <input
              type="text"
              value={formData.interaction_type || ''}
              onChange={(e) => dispatch(updateField({ interaction_type: e.target.value }))}
              placeholder="e.g. In-Person"
            />
          </div>
          <div className="form-group">
            <label>Meeting Summary</label>
            <textarea
              rows="5"
              value={formData.summary || ''}
              onChange={(e) => dispatch(updateField({ summary: e.target.value }))}
              placeholder="Describe the meeting..."
            />
          </div>
          <div className="form-group">
            <label>Agent Sentiment Analysis</label>
            <input
              type="text"
              value={formData.sentiment || ''}
              onChange={(e) => dispatch(updateField({ sentiment: e.target.value }))}
              placeholder="Sentiment..."
            />
          </div>
          <button
            className="submit-btn"
            onClick={async () => {
              try {
                // Direct call to log the current form data
                await axios.post('http://localhost:8000/chat', {
                  message: `Log this interaction for ${formData.hcp_name}: ${formData.summary}`
                });
                alert("Interaction logged successfully!");
              } catch (err) {
                alert("Error saving interaction.");
              }
            }}
            style={{
              marginTop: '20px',
              padding: '10px 20px',
              backgroundColor: '#2563eb',
              color: 'white',
              border: 'none',
              borderRadius: '5px',
              cursor: 'pointer'
            }}
          >
            Save Interaction
          </button>
        </div>

        {/* RIGHT: AI CHAT INTERFACE */}
        <div className="chat-section">
          <h3>Conversational AI Agent</h3>
          <div className="chat-window">
            {formData.chatHistory.map((msg, i) => (
              <div key={i} className={`msg ${msg.role}`}>{msg.content}</div>
            ))}
          </div>
          <div className="input-area">
            <input
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              placeholder="Tell the agent about your meeting..."
            />
            <button onClick={handleChatSubmit}>Send</button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;