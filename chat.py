# chat.py

import streamlit as st
from dotenv import load_dotenv
from llm import get_ai_response

st.set_page_config(page_title="무역관 정산 챗봇", page_icon="💰")
st.title("💰무역관 정산 챗봇")
st.caption("해외무역관 정산에 대한 모든 것을 물어보세요!")

load_dotenv()

# --- 이전 대화 기록과 출처를 함께 출력 ---
if 'message_list' not in st.session_state:
    st.session_state.message_list = []

for message in st.session_state.message_list:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if message["role"] == "ai" and "source" in message and message["source"]:
            st.caption(message["source"])


# --- 사용자가 질문을 입력했을 때의 처리 ---
if user_question := st.chat_input(placeholder="해외무역관 정산에 대한 궁금한 내용을 물어보세요"):
    st.session_state.message_list.append({"role": "user", "content": user_question})
    st.session_state.message_list.append({"role": "ai", "content": "", "source": None})
    st.rerun()


# --- 화면을 다시 그린 후, 마지막 메시지가 AI의 빈 답변일 경우에만 스트리밍 실행 ---
# 리스트가 비어있지 않고, 마지막 메세지가 ai이고, 그 내용이 비어 있으면 답변 생성 로직을 실행
if st.session_state.message_list and st.session_state.message_list[-1]["role"] == "ai" and st.session_state.message_list[-1]["content"] == "":
    
    # 가장 마지막 사용자 질문을 가져옴
    user_question = st.session_state.message_list[-2]["content"]
    
    with st.spinner("답변을 생성하는 중입니다..."): # 출력
        ai_response_stream = get_ai_response(user_question)

        full_answer = ""
        source_info = None
        
        # 스트리밍 처리
        for chunk in ai_response_stream:
            if "context" in chunk and source_info is None:
                first_doc = chunk["context"][0] # 첫번째 데이터만
                if hasattr(first_doc, 'metadata'):
                    page_num = int(first_doc.metadata.get("page_num", 0))
                    pdf_name = first_doc.metadata.get("origin_pdf", "없음")
                    source_info = f"📄 출처: {page_num}p / {pdf_name}"
            
            if "answer" in chunk:
                full_answer += chunk["answer"]
        
        # session_state의 마지막 AI 메시지를 완성된 내용으로 업데이트
        st.session_state.message_list[-1]["content"] = full_answer
        st.session_state.message_list[-1]["source"] = source_info
        
        # 화면을 다시 그려서 최종 결과를 표시
        st.rerun()