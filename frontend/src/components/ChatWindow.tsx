import React from 'react';
import ChatInput from './ChatInput';

const ChatWindow = () => (
  <div>
    <div className=" flex flex-1 items-center justify-center">
        <h2 className ='text-xl md:text-3xl font-semibold text-white'>What's on the agenda today?</h2>
    </div>
    <div>
        <ChatInput/>
    </div>
  </div>
);

export default ChatWindow;