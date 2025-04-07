import streamlit as st
import openai
import os

# تحديد مفتاح الـ API: نستخدم st.secrets إن وجد، وإلا نطلب من المستخدم إدخاله.
if "OPENAI_API_KEY" in st.secrets:
    openai_api_key = st.secrets["OPENAI_API_KEY"]
else:
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    if not openai_api_key:
        st.info("يرجى إدخال مفتاح OpenAI API للمتابعة.", icon="🗝️")
        st.stop()

openai.api_key = openai_api_key

# اختيار الوضع بين Chatbot و"القاضي الذكي" عبر شريط جانبي
mode = st.sidebar.radio("اختر الوضع", ["Chatbot", "القاضي الذكي"])

if mode == "Chatbot":
    st.title("💬 Chatbot")
    st.write(
        "هذا التطبيق يستخدم نموذج GPT-3.5 لإنشاء الردود. يمكنك التفاعل مع الدردشة بشكل مباشر."
    )

    # حفظ الرسائل في الجلسة لضمان استمرارها عبر التحديثات
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # عرض الرسائل السابقة باستخدام st.chat_message
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # حقل إدخال الدردشة
    user_input = st.chat_input("ما الجديد؟")
    if user_input:
        # إضافة رسالة المستخدم للرسائل الموجودة
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # استدعاء OpenAI API مع البث (stream) لعرض الرد تدريجيًا
        response_placeholder = st.empty()
        full_response = ""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=st.session_state.messages,
                stream=True,
            )
            with st.chat_message("assistant"):
                for chunk in response:
                    chunk_message = chunk["choices"][0]["delta"].get("content", "")
                    full_response += chunk_message
                    response_placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"❌ حدث خطأ: {e}")

elif mode == "القاضي الذكي":
    st.title("القاضي الذكي")
    st.write("أدخل الاستفسار وتفاصيل القضية لتحليلها.")
    
    # حقول إدخال لاستفسار القضية وتفاصيلها
    inquiry = st.text_input("الاستفسار:")
    case_text = st.text_area("تفاصيل القضية:")

    def analyze_case(inquiry, case_text):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "أنت قاضٍ ذكي تقوم بتحليل القضايا."},
                {"role": "user", "content": f"الاستفسار: {inquiry}\nتفاصيل القضية: {case_text}"}
            ]
        )
        return response.choices[0].message["content"]

    # عند الضغط على زر "تحليل القضية" يتم استدعاء الدالة وعرض النتيجة
    if st.button("تحليل القضية"):
        st.write("جارٍ تحليل القضية...")
        try:
            result = analyze_case(inquiry, case_text)
            st.success(result)
        except Exception as e:
            st.error(f"❌ حدث خطأ: {e}")
