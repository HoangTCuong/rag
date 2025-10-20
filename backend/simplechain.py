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


template = """<|im_start|>system\nSử dụng thông tin sau đây để trả lời câu hỏi. Nếu bạn không biết câu trả lời, hãy nói không biết, đừng cố tạo ra câu trả lời. 
                Câu trả lời của bạn hãy trình bày dưới dạng 1 văn bản\n{context}<|im_end|>\n<|im_start|>user\n{question}<|im_end|>\n<|im_start|>assistant"""
prompt = create_prompt(template)

llm = load_llm(model_file)

# ⚙️ Tạo "chain" bằng Runnable
parser = StrOutputParser()
chain = prompt | llm | parser

# 🧠 Gọi chuỗi
context = """
     "mạch suy nghĩ của tác giả, không làm trở ngại việc đọc ĐAKLTN;",
        "- Số trang được đánh ở giữa, phía trên đầu mỗi trang giấy, từ phần Mở đầu đến",
        "cần mở rộng tờ giấy và tránh bị đóng vào gáy của ĐAKLTN phần mép giấy bên trong",
        "thập thông tin cần mô tả: phương pháp chọn mẫu, cách tiếp cận đối tượng khảo sát, cách",
        "quyết như: khái niệm, định nghĩa, đặc điểm, phân loại, ... các quan điểm, trường phái,",
        "ĐAKLTN phải được trình bày ngắn gọn, rõ ràng, mạch lạc, sạch sẽ, không được",
        "yếu nhằm thừa nhận nguồn của những ý tưởng có giá trị và giúp người đọc theo được",
        "trong ngoặc đơn đặt bên phía lề phải. Nếu một nhóm phương trình mang cùng một số",
        "dẫn, sử dụng và đề cập tới để bàn luận trong ĐAKLTN;",
        "Đối với một số chuyên ngành, phần Thực trạng… có thể để riêng thành một"
"""
question = "Tôi cần trình bày bố cục như thế nào?"

response = chain.invoke({
    "question": question,
    "context": context
})

print(response)