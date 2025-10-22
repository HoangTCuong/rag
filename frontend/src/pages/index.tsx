import React from 'react';
import Header from '../components/Header';
import Sidebar from '../components/Sidebar';
import ChatWindow from '@/components/ChatWindow';

const Home = () => {
  return (
    <div className="flex">
      <div className='bg-black text-gray-200 max-w-[250px] min-w-[220px] h-screen'>
        <Sidebar />
      </div>
      <div className="bg-[#2f2f2f] w-full min-h-screen text-gray-200 flex flex-col">
        <Header />
        <div className="flex-1 flex items-center justify-center">
          <ChatWindow />
        </div>
      </div>
    </div>
  );
};

export default Home;