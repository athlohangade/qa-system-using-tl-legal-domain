import os 
import sys
sys.path += ['./']
import random
import streamlit as st
from Main import Main


@st.cache(suppress_st_warning=True, allow_output_mutation=True, show_spinner=False)
def get_contexts(doc_name) :

    contexts = Main.get_contexts_given_the_doc(doc_name)
    return contexts


@st.cache(suppress_st_warning=True, allow_output_mutation=True, show_spinner=False)
def generate_questions(contexts) :

    generated_questions_and_contexts = Main.get_questions_given_the_contexts(contexts)
    return generated_questions_and_contexts


@st.cache(suppress_st_warning=True, allow_output_mutation=True, show_spinner=False)
def get_answers_for_questions(generated_questions_and_contexts) :

    answers = Main.get_answer_given_the_question_and_context_list(generated_questions_and_contexts)
    return answers


@st.cache(suppress_st_warning=True, allow_output_mutation=True, show_spinner=False)
def generate_answer_for_the_question(question, contexts) :

    answer = Main.get_answer_for_single_question_given_context_list(question, contexts)
    return answer



# Print the title
st.title("Question Answering system for Legal Documents")
st.write("---")

# Select the Mode of Operation
st.header("Select the mode of operation :")
modes = ['Generate and Answer Question on Document', 'Answer Question on Document']
mode_of_operation = st.radio("", range(len(modes)), format_func = lambda x: modes[x])

if mode_of_operation == 0 :

    # Print the dropdown list for selecting the doc
    st.header("Select a Legal Document :")
    st.write(" ")
    legal_docs_names = os.listdir("./legal_docs/")
    legal_docs_names = [i for i in legal_docs_names if i[-4:] == ".pdf"]
    legal_docs_names = ["Select Act"] + legal_docs_names
    doc_name = st.selectbox("", [legal_doc.replace(".pdf", "") for legal_doc in legal_docs_names])

    uploaded_file = st.file_uploader("Choose a file", type = 'pdf')
    if uploaded_file is not None :
        with open(f"./legal_docs/uploads/{uploaded_file.name}", "wb") as f:
            f.write(uploaded_file.getbuffer())
        doc_name = "uploads/" + uploaded_file.name[:-4]

    if doc_name != "Select Act" :

        doc_name = "./legal_docs/" + doc_name + ".pdf"
        contexts = get_contexts(doc_name)

        st.write(" ")
        if st.button("Generate more samples") :
            random.shuffle(contexts)

        contexts = contexts[:3]
        with st.spinner("Generating Questions...") :
            generated_questions_and_contexts = generate_questions(contexts)
        with st.spinner("Finding Answers...") :
            answers = get_answers_for_questions(generated_questions_and_contexts)

        # List the generated questions
        st.header("Generated Questions :")
        st.write(" ")
        question_numbers = list(range(len(generated_questions_and_contexts)))
        selected_question = st.selectbox("", question_numbers, \
            format_func = lambda x: generated_questions_and_contexts[x][0])

        # Print the selected question
        st.header("Question :")
        st.markdown("---\n" f"{generated_questions_and_contexts[selected_question][0]}\n\n" "---")

        # Print the answer
        st.header("Answer :")
        st.markdown("---\n" f"{answers[selected_question]}\n\n" "---")

        # Print the context corresponding to that answer
        st.header("Context :")
        st.markdown("---\n" f"{generated_questions_and_contexts[selected_question][1]}\n\n" "---")


elif mode_of_operation == 1 :

     # Print the dropdown list for selecting the doc
    st.header("Select a Legal Document :")
    st.write(" ")
    legal_docs_names = os.listdir("./legal_docs/")
    legal_docs_names = [i for i in legal_docs_names if i[-4:] == ".pdf"]
    legal_docs_names = ["Select Act"] + legal_docs_names
    doc_name = st.selectbox("", [legal_doc.replace(".pdf", "") for legal_doc in legal_docs_names])

    uploaded_file = st.file_uploader("Choose a file", type = 'pdf')
    if uploaded_file is not None :
        with open(f"./legal_docs/uploads/{uploaded_file.name}", "wb") as f:
            f.write(uploaded_file.getbuffer())
        doc_name = "uploads/" + uploaded_file.name[:-4]

    if doc_name != "Select Act" :

        st.header("Enter the Question :")
        question = st.text_area("")

        doc_name = "./legal_docs/" + doc_name + ".pdf"
        contexts = get_contexts(doc_name)

        st.write(" ")
        if st.button("Get the Answer") :

            with st.spinner("Finding the Answer...") :
                answer = generate_answer_for_the_question(question, contexts)

            # Print the answer
            st.header("Answer :")
            st.markdown("---\n" f"{answer}\n\n" "---")

        contexts = contexts[:3]
        with st.spinner("Finding some suggestions...") :
            generated_questions_and_contexts = generate_questions(contexts)
            answers = get_answers_for_questions(generated_questions_and_contexts)

        st.header("Some suggested questions :")
        st.write(" ")
        question_numbers = list(range(len(generated_questions_and_contexts)))
        selected_question = st.selectbox("", question_numbers, \
            format_func = lambda x: generated_questions_and_contexts[x][0])

        # Print the selected question
        st.header("Question :")
        st.markdown("---\n" f"{generated_questions_and_contexts[selected_question][0]}\n\n" "---")

        # Print the answer
        st.header("Answer :")
        st.markdown("---\n" f"{answers[selected_question]}\n\n" "---")