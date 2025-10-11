// filepath: /Users/cuonghoang/Desktop/VSCode/gptclone/my-app/src/components/Header.tsx
import React from 'react';
import Link from 'next/link';
import { FaAngleDown } from "react-icons/fa";

const Header = () => {
  return (
    <div className='flex items-center justify-between m-2.5 h-10 sticky w-full top-0 left-0 pl-2 pr-12'>
        <button className='flex items-center gap-1 bg-[#2f2f2f] rounded-sm p-1 hover:bg-[#3f3f3f]'>Model <FaAngleDown /></button>
        <Link className='text-gray-200' href={"/signin"}>Sign in</Link>
    </div>
  )
}

export default Header;