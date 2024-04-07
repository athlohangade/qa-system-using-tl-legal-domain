# Question Answering system using Transfer Learning for legal documents

## Introduction

Question Answer System (QAS) is one of the key tasks of Natural Language Processing (NLP), with wide applications in language based AI Systems. A general QAS tries to answer a question by referring the provided context as a knowledge source. Further, recently, there has been significant progress in [Transfer Learning](https://en.wikipedia.org/wiki/Transfer_learning) techniques that attempts to use the knowledge gained from one task and apply it to another related task in order to either increase efficiency or reduce the size of the domain-specific dataset.

This repo is about implementing a closed domain QAS for Legal Documents, particularly Legal Acts, following a Transfer Learning approach. The Legal Acts amended by the Indian Constitution and Judiciary, used for this project is available [here](https://www.indiacode.nic.in/).

## System Design

The system has three components: Preprocessing and Context Creation, Question Generation (QG) and Question Answering.

1. *Preprocessing and Context Creation* : A typical legal act consists of the title of the act, index pages, chapters, sections, subsections and footer notes. The important information is found in the sections and subsections which serve as good context. Hence, pre-processing is needed to filter the data and to ensure that only the most relevant content is extracted. It involves converting PDF format data to plain text, removing index pages, locating the first main content page, removing the title, eliminating the unwanted symbols, deleting the chapter headers and discarding the footer notes if any. The text is divided into chunks of not more than 350 words retaining the subsection boundaries which form the *contexts*.

2. *Question Generation* : Question Generation is an auxiliary component of the system to demonstrate generation of machine-generated questions in absence of the actual user query in real time and also to build a legal dataset required for fine-tuning. For this, Google T5-base is used which is available [here](https://huggingface.co/mrm8488/t5-base-finetuned-squadv2). The pre-processed contexts are given as input to QG which finds possible answer spans and generates questions for those spans.

3. *Question Answering* :  The QAS uses the BERT-Large model fine-tuned on legal domain dataset. The answer to the question is found following batch processing technique with a batch size of 32. Given a question and list of contexts, the model generates a list of start and end scores for each context which represents the answer spans. The best context answer is determined using a final score which is calculated as the sum of the start and end scores for the answer.

## Fine-Tuning

The pretrained BERT-Large is fine-tuned on legal domain dataset. The fine-tuned BERT-Large model is available [here](https://huggingface.co/atharvamundada99/bert-large-question-answering-finetuned-legal). The legal dataset consists of both machine-generated questions from QG model and human-generated questions. The Legal Dataset is split in the percentage of 80% train set, 10% validation set, and 10% test set. It is available under *'Datasets'* directory of the repo. The training is done in 4 epochs at a learning rate of 2e-5 with batch size of 16 dataset items. The code for fine-tuning is available under *'System Components'* directory of the repo.

## Evaluation

The system is evaluated using the metrics : Exact Match, F1 and Weighted Accuracy. Exact Match is the percentage of questions which are answered perfectly. F1 is defined as the harmonic mean of precision and recall. Weighted-Accuracy is the ratio of sum of weights of the answers of the questions to the total number of questions, expressed as a percentage. For each question, a weight between 0 and 4 is assigned depending on how well the answer matches to the actual answer. The QAS achieved Weighted Accuracy value of 84.2262, Exact Match score of 77.381 and F1-score of 76.2579.

## Mode of operation

The system can be work in two modes :

1. *generate-and-answer-question-on-document* : In this mode, the system expects a legal document as input, and automatically generates a set of questions on the inputted document using the QG component. The user can then select any question from this list of generated questions to get a specific answer from the QA system. This is useful when user doesn't have his/her own questions and just intends to test the model.

2. *answer-question-on-document* : In this mode, the system expects both a document and a question related to that document from the user as input. QAS answers the inputted user's question. Here the user question replaces the QG component for the question part. Moreover, the system also generates some suggested questions on the document, using the QG component to aid the user if he/she is unaware about what should be asked.

## Usage

The project source files are available under *'src'*. The project can be run on local system after installing all the requirements using the following command :

    streamlit run app.py

The project can also be used by directly running the *project_qas.ipynb* file in google colab which is present under *'System Components'* directory of the repo (Don't forget to upload the zipped src folder in colab before running).

The project uses [Streamlit](https://streamlit.io/) python library for simple intuitive user interface.

## Authors

[Atharva Lohangade](https://github.com/athlohangade/)

[Atharva Mundada](https://github.com/atharvamundada99)

[Manas Joshi](https://github.com/manasjoshi76)
