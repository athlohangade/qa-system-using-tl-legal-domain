import os 
import streamlit as st

# Print the title
st.title("Question Answering system for Legal Documents")
st.write("---")

# Print the dropdown list for selecting the doc
st.subheader("Choose a legal doc :")
st.write(" ")
legal_docs_names = os.listdir("./legal_docs/")
# for i in range(len(legal_docs_names)) :
#     legal_docs_names[i] = legal_docs_names[i].replace(".pdf", "")
st.selectbox("", [legal_doc.replace(".pdf", "") for legal_doc in legal_docs_names])

# Print the generated questions
# Here call the function to get the questions and contexts for those questions
generated_questions_and_contexts = [['question1', 'context1'], ['question2', 'context2']]
st.subheader("List of generated questions :")
st.write(" ")
question_numbers = list(range(len(generated_questions_and_contexts)))
selected_question = st.selectbox("", question_numbers, \
    format_func = lambda x: generated_questions_and_contexts[x][0])

# Print the selected question
st.subheader("Question :")
st.text_area("", generated_questions_and_contexts[selected_question][0])

# Print the context corresponding to that answer
st.subheader("Context :")
st.text_area("", generated_questions_and_contexts[selected_question][1])

# Print the context corresponding to that answer
# Here call the function to get the answer, given the context and question
answer = "answer1"
st.subheader("Answer :")
st.text_area("", answer)
