export interface ChatMessage {
  id: string;
  sender: string;
  content: string;
  timestamp: Date;
}

export interface User {
  id: string;
  name: string;
  email: string;
}

export interface ChatInputProps {
  onSend: (message: string) => void;
}

export interface ChatWindowProps {
  messages: ChatMessage[];
}

export interface SidebarProps {
  onSelectModel: (model: string) => void;
}