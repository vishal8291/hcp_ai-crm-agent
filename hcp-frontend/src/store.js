import { configureStore, createSlice } from '@reduxjs/toolkit';

const interactionSlice = createSlice({
  name: 'interaction',
  initialState: {
    hcp_name: '',
    interaction_type: '',
    summary: '',
    sentiment: '',
    next_step: '',
    chatHistory: []
  },
  reducers: {
    updateField: (state, action) => {
      return { ...state, ...action.payload };
    },
    addChatMessage: (state, action) => {
      state.chatHistory.push(action.payload);
    }
  }
});

export const { updateField, addChatMessage } = interactionSlice.actions;
export const store = configureStore({ reducer: { interaction: interactionSlice.reducer } });