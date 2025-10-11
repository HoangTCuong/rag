import React, { useRef, useState } from 'react';
import { FiPlus, FiMic, FiSend } from 'react-icons/fi';

const ChatInput = () => {
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [fileName, setFileName] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null);
    setSuccess(null);
    const file = e.target.files?.[0];
    if (!file) return;
    setFileName(file.name);
    if (file.type !== "application/pdf") {
      setError("Chỉ hỗ trợ upload file PDF.");
      return;
    }
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);

      const res = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        throw new Error("Upload thất bại.");
      }
      setSuccess("Upload thành công!");
    } catch (err) {
      setError("Có lỗi xảy ra khi upload.");
    } finally {
      setUploading(false);
    }
  };

  const handleChooseFile = () => {
    fileInputRef.current?.click();
  };

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