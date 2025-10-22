import React from 'react';
import { IoCreateOutline } from "react-icons/io5";


const Sidebar = () => {
  return (
    <>
      <ul>
        <li className='flex gap-1 items-center m-2.5'> <IoCreateOutline  /> New chat</li>
        <li className='m-2.5'>Chat history</li>
      </ul>
    </>
  );
}

export default Sidebar;