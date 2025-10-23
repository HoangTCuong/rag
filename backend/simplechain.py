from langchain_community.llms import CTransformers
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


#cau hinh
model_file = "model/vinallama-7b-chat_q5_0.gguf"

#Load model
def load_llm(model_file):
    llm = CTransformers(
        model=model_file,
        model_type = "llama",
        max_new_tokens = 1024,
        temperature = 0.05
    )
    return llm

#tạo prompt template
def create_prompt(template):
    prompt = PromptTemplate(template = template, input_variables = ["context", "question"])
    return prompt


template = """
    <|im_start|>system
    Bạn là trợ lý AI chính xác và trung thực. 
    Chỉ dùng thông tin trong {context} để trả lời. 
    Nếu không đủ dữ liệu, hãy nói: "Tôi không có đủ thông tin để trả lời câu hỏi này."
    Không suy đoán hay bịa đặt. 
    Trả lời ngắn gọn, rõ ràng, bằng ngôn ngữ tự nhiên, trình bày khoa học.
    <|im_end|>
    <|im_start|>user
    {question}
    <|im_end|>
    <|im_start|>assistant
"""
prompt = create_prompt(template)

llm = load_llm(model_file)

# ⚙️ Tạo "chain" bằng Runnable
parser = StrOutputParser()
chain = prompt | llm | parser

# 🧠 Gọi chuỗi
context = """
        "chính mà ĐAKLTN đã trình bày:",
        "- Tóm tắt ĐAKLTN: trình bày cô đọng, súc tích nội dung và kết quả dưới 20 dòng; Formatted: Vietnamese",
        "Các mục của ĐAKLTN được trình bày và đánh số thành nhóm số, nhiều nhất Vietnamese",
        "ĐAKLTN phải được trình bày ngắn gọn, rõ ràng, mạch lạc, sạch sẽ, không được",
        "phải được trình bày về cách vận dụng cụ thể trong đề tài.",
        "thức thiết kế bảng câu hỏi, ... Trình bày PPNC phải đảm bảo hai yêu cầu quan trọng là:",
        "- MỞ ĐẦU: trình bày lý do chọn đề tài, mục đích, đối tượng và phạm vi nghiên Formatted: Font color: Text 1, Vietnamese",
        "tài liệu thì ĐAKLTN không được duyệt để bảo vệ;",
        "hình vẽ, công thức, đồ thị, phương trình, ý tưởng... ) mà không chú dẫn tác giả và nguồn",
        "+ Trình bày kết quả thu được theo mục tiêu của nghiên cứu. Các số liệu phải Formatted: Font color: Text 1, Vietnamese"
"""
question = "Giải thích cho tôi ma trận vuông là gì?"

response = chain.invoke({
    "question": question,
    "context": context
})

print(response)