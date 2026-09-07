import os
import streamlit as st
from dotenv import load_dotenv
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

st.set_page_config(page_title="Smart PDF Chat Assistant", layout="wide")

st.title("📄 AI-Powered Document Chat Assistant (RAG)")
st.write("PDF फाइल अपलोड गर्नुहोस् र च्याट मार्फत प्रश्नहरूको उत्तर पाउनुहोस्!")

# साइडबार कन्फिगरेसन
st.sidebar.header("Configuration")
user_api_key = st.sidebar.text_input("Enter your Google Gemini API Key:", type="password")

if user_api_key:
    os.environ["GOOGLE_API_KEY"] = user_api_key
elif api_key:
    os.environ["GOOGLE_API_KEY"] = api_key

# PDF अपलोड अप्सन
uploaded_file = st.file_uploader("एउटा PDF फाइल अपलोड गर्नुहोस्", type=["pdf"])

if uploaded_file is not None:
    if not os.environ.get("GOOGLE_API_KEY"):
        st.warning("कृपया आफ्नो Google Gemini API Key प्रविष्ट गर्नुहोस्।")
    else:
        # अस्थायी फाइल सेभ गर्ने
        with open("temp.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        @st.cache_resource
        (_file_path="temp.pdf")
        def load_vectorstore(_file_path):
            loader = PyPDFLoader(_file_path)
            docs = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            splits = text_splitter.split_documents(docs)
            
            embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-2-preview")
            vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
            return vectorstore

        with st.spinner("PDF प्रोसेस हुँदैछ..."):
            vectorstore = load_vectorstore("temp.pdf")
            retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
            llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash", temperature=0.3)

            system_prompt = (
                "तपाईं एक उपयोगी AI सहायक हुनुहुन्छ। तल दिइएको सन्दर्भ (context) को प्रयोग गरेर मात्र प्रश्नको उत्तर दिनुहोस्। "
                "यदि तपाईंलाई उत्तर थाहा छैन भने, 'मलाई यो कागजातमा भेटिएन' भन्नुहोस्。\n\n"
                "{context}"
            )
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "{input}"),
            ])

            question_answer_chain = create_stuff_documents_chain(llm, prompt)
            rag_chain = create_retrieval_chain(retriever, question_answer_chain)

        st.success("PDF सफलतापूर्वक प्रोसेस भयो! अब तल च्याट गर्नुहोस्।")

        # च्याट हिस्ट्री राख्ने स्टेट (Session State)
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # पुराना मेसेजहरू स्क्रिनमा देखाउने
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # युजरको नयाँ इनपुट लिने
        if user_query := st.chat_input("यो कागजातको बारेमा केही सोध्नुहोस्..."):
            st.session_state.messages.append({"role": "user", "content": user_query})
            with st.chat_message("user"):
                st.markdown(user_query)

            with st.chat_message("assistant"):
                with st.spinner("उत्तर खोज्दैछ..."):
                    response = rag_chain.invoke({"input": user_query})
                    answer = response["answer"]
                    st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})

        if os.path.exists("temp.pdf"):
            os.remove("temp.pdf")