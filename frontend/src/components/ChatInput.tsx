import React, { useRef, useState } from 'react';
import { FiPlus, FiMic, FiSend } from 'react-icons/fi';

const ChatInput = () => {
  const [fileName, setFileName] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleChooseFile = () => {
    fileInputRef.current?.click();
  }

  const handleFileChange = async (e) => {
    const file = e.target.file?.[0];
    if (!file) return;

    setFileName(file.name);
    setError("");
    setSuccess("");

    if (file.type !== "application/pdf") {
      setError("Chi nhan upload file pdf thoi ban oi!");
      return;
    }

    setUploading(true);
  }

  

  return (
    <div className="w-full flex flex-col items-center px-2 py-3 bg-transparent">
      <div className="flex items-center w-full max-w-2xl mx-auto bg-[#232323] rounded-full px-4 py-2 shadow-md">
        <button
          className="text-gray-400 hover:text-white mr-2"
          onClick={handleChooseFile}
          type="button"
        >
          <FiPlus size={20} />
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept="application/pdf"
          className="hidden"
          onChange={handleFileChange}
          disabled={uploading}
        />
        <input
          className="flex-1 bg-transparent outline-none text-gray-200 placeholder-gray-400 px-2"
          type="text"
          placeholder="How can I help you?"
        />
        <button className="text-gray-400 hover:text-white">
          <FiSend size={20} />
        </button>
      </div>
      <div className="w-full max-w-2xl mt-2 flex flex-col items-start">
        {fileName && (
          <p className="text-gray-300 mb-1">Đã chọn: <span className="font-medium">{fileName}</span></p>
        )}
        {uploading && <p className="text-gray-400 mb-1">Đang upload...</p>}
        {error && <p className="text-red-400 mb-1">{error}</p>}
        {success && <p className="text-green-400 mb-1">{success}</p>}
      </div>
    </div>
  );
};

export default ChatInput;