# Import required libraries
import os 
import sys
sys.path += ['./']
import random
import streamlit as st
from Main import Main

# Function to get the contexts given the doc name. Returns the cached entry if available,
# else make the required function call
@st.cache(suppress_st_warning=True, allow_output_mutation=True, show_spinner=False)
def get_contexts(doc_name) :

    contexts = Main.get_contexts_given_the_doc(doc_name)
    return contexts

# Function to generate the questions given the contexts. Returns the cached entry if available,
# else make the required function call
@st.cache(suppress_st_warning=True, allow_output_mutation=True, show_spinner=False)
def generate_questions(contexts) :

    generated_questions_and_contexts = Main.get_questions_given_the_contexts(contexts)
    return generated_questions_and_contexts

# Function to find the answers given the contexts and questions. Returns the cached entry if available,
# else make the required function call. Machine generated questions case.
@st.cache(suppress_st_warning=True, allow_output_mutation=True, show_spinner=False)
def get_answers_for_questions(generated_questions_and_contexts) :

    answers = Main.get_answer_given_the_question_and_context_list(generated_questions_and_contexts)
    return answers

# Function to find the answer given a question and list of contexts. Returns the cached entry if available,
# else make the required function call. User inputted questions case.
@st.cache(suppress_st_warning=True, allow_output_mutation=True, show_spinner=False)
def generate_answer_for_the_question(question, contexts) :

    answer = Main.get_answer_for_single_question_given_context_list(question, contexts)
    return answer


# Print the title
st.title("Question Answering System for Legal Documents")
st.write("---")

# Select the Mode of Operation
st.header("Mode of Operation")
modes = ['Generate and Answer Question on Document', 'Answer Question on Document']
mode_of_operation = st.radio("", range(len(modes)), format_func = lambda x: modes[x])

# If first mode is selected
if mode_of_operation == 0 :

    st.header("Select a Legal Document")
    st.write(" ")
    # Get the legal acts titles
    legal_docs_names = os.listdir("./legal_docs/")
    legal_docs_names = [i for i in legal_docs_names if i[-4:] == ".pdf"]
    legal_docs_names = ["Select Act"] + legal_docs_names
    # Dropdown list widget for selecting the document
    doc_name = st.selectbox("", [legal_doc.replace(".pdf", "") for legal_doc in legal_docs_names])

    # Upload widget for letting the user upload the document
    uploaded_file = st.file_uploader("Choose a file", type = 'pdf')
    if uploaded_file is not None :
        # Save the file on our server
        with open(f"./legal_docs/uploads/{uploaded_file.name}", "wb") as f:
            f.write(uploaded_file.getbuffer())
        doc_name = "uploads/" + uploaded_file.name[:-4]

    # If user selects any document
    if doc_name != "Select Act" :

        # Get the contexts from the selected document
        doc_name = "./legal_docs/" + doc_name + ".pdf"
        contexts = get_contexts(doc_name)

        # If user wants more samples, shuffle the contexts to skip the cached entries
        st.write(" ")
        if st.button("More Samples") :
            random.shuffle(contexts)

        # Use the first 3 contexts of the list for generating questions and answers
        contexts = contexts[:3]
        with st.spinner("Generating Questions...") :
            generated_questions_and_contexts = generate_questions(contexts)
        with st.spinner("Finding Answers...") :
            answers = get_answers_for_questions(generated_questions_and_contexts)

        # List the generated questions
        st.header("Generated Questions")
        st.write(" ")
        question_numbers = list(range(len(generated_questions_and_contexts)))
        selected_question = st.selectbox("", question_numbers, \
            format_func = lambda x: generated_questions_and_contexts[x][0])

        # Print the selected question
        st.header("Question")
        st.markdown("---\n" f"<div style='text-align: justify'>{generated_questions_and_contexts[selected_question][0]}</div>\n\n" "---", unsafe_allow_html=True)

        # Print the answer
        st.header("Answer")
        st.markdown("---\n" f"<div style='text-align: justify'>{answers[selected_question]}</div>\n\n" "---", unsafe_allow_html=True)

        # Print the context corresponding to that answer
        st.header("Context")
        st.markdown("---\n" f"<div style='text-align: justify'>{generated_questions_and_contexts[selected_question][1]}</div>\n\n" "---", unsafe_allow_html=True)

# If second mode is selected
elif mode_of_operation == 1 :

    st.header("Select a Legal Document")
    st.write(" ")
    # Get the legal acts titles
    legal_docs_names = os.listdir("./legal_docs/")
    legal_docs_names = [i for i in legal_docs_names if i[-4:] == ".pdf"]
    legal_docs_names = ["Select Act"] + legal_docs_names
    # Dropdown list widget for selecting the document
    doc_name = st.selectbox("", [legal_doc.replace(".pdf", "") for legal_doc in legal_docs_names])

    # Upload widget for letting the user upload the document
    uploaded_file = st.file_uploader("Choose a file", type = 'pdf')
    if uploaded_file is not None :
        # Save the file on our server
        with open(f"./legal_docs/uploads/{uploaded_file.name}", "wb") as f:
            f.write(uploaded_file.getbuffer())
        doc_name = "uploads/" + uploaded_file.name[:-4]

    # If user selects any document
    if doc_name != "Select Act" :

        # UI widget to input the question from the user
        st.header("Enter the Question")
        question = st.text_area("")

        # Get the contexts from the selected document
        doc_name = "./legal_docs/" + doc_name + ".pdf"
        contexts = get_contexts(doc_name)

        # Find the answer to the user's question
        st.write(" ")
        if st.button("Get Answer") :

            # Get the answer for the user inputted question and context list
            with st.spinner("Finding the Answer...") :
                answer = generate_answer_for_the_question(question, contexts)

            # If answer is predicted with some positive confidence score
            if answer[2] > 0 :
                # Print the answer
                st.header("Answer")
                st.markdown("---\n" f"<div style='text-align: justify'>{answer[0]}</div>\n\n" "---", unsafe_allow_html=True)

                # Print the context
                st.header("Context")
                st.markdown("---\n" f"<div style='text-align: justify'>{answer[1]}</div>\n\n" "---", unsafe_allow_html=True)

                # Print the confidence value of the answer
                st.markdown(f"**Confidence value :** {answer[2]} %\n\n" "---")

            # If the confidence score is zero or negative
            else :
                # Print the answer
                st.header("Answer")
                st.markdown("---\n" "<div style='text-align: justify'><i>No answer</i></div>\n\n" "---", unsafe_allow_html=True)

        # If more suggestions are expected, shuffle the contexts to skip the cached entries
        st.write(" ")
        if st.button("More Suggestions") :
            random.shuffle(contexts)

        # Use the first 3 contexts of the list for generating questions and answers
        contexts = contexts[:3]
        with st.spinner("Finding some Suggestions...") :
            generated_questions_and_contexts = generate_questions(contexts)
            answers = get_answers_for_questions(generated_questions_and_contexts)

        # Print the suggested questions
        st.header("Suggested Pool of Questions")
        st.write(" ")
        question_numbers = list(range(len(generated_questions_and_contexts)))
        selected_question = st.selectbox("", question_numbers, \
            format_func = lambda x: generated_questions_and_contexts[x][0])

        # Print the selected question
        st.header("Question")
        st.markdown("---\n" f"<div style='text-align: justify'>{generated_questions_and_contexts[selected_question][0]}</div>\n\n" "---", unsafe_allow_html=True)

        # Print the answer
        st.header("Answer")
        st.markdown("---\n" f"<div style='text-align: justify'>{answers[selected_question]}</div>\n\n" "---", unsafe_allow_html=True)

        # Print the context corresponding to that answer
        st.header("Context")
        st.markdown("---\n" f"<div style='text-align: justify'>{generated_questions_and_contexts[selected_question][1]}</div>\n\n" "---", unsafe_allow_html=True)