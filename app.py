# from utils.utils import load_and_store_file, load_vector_store, get_hf_llm, store_documents, load_and_split_documents

import streamlit as st
from dotenv import load_dotenv
import requests as r 
from chat.chatbot import HuggingInferenceEndpointLLM
from chat.prompts import SNOOP_PROMPT
from chat.tts import text_to_speech, Client, options

def load_llm_and_chain():
    if 'llm' not in st.session_state.keys():
        
        hf_llm = HuggingInferenceEndpointLLM(hf_model_or_api_url=st.secrets['SNOOP_LLM_API_ENDPOINT'], 
                                             hf_token=st.secrets['HF_TOKEN'],
                                                temperature=0.8, 
                                                repetition_penalty=1.1, 
                                                max_new_tokens=1000)
        
        st.session_state['llm'] = hf_llm    
        
    if 'chain' not in st.session_state.keys():    
        chain = SNOOP_PROMPT | hf_llm
        st.session_state['chain'] = chain


def initialize_endpoint():

    import time
    
    headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}",
                "Content-Type": "application/json"}

    def get_status(url=st.secrets['SNOOP_LLM_API_ENDPOINT'], 
                   headers=headers):
        res = r.get(url,  headers=headers)
        return res.status_code
    
    def initial_message(url=st.secrets['SNOOP_LLM_API_ENDPOINT'], 
                             headers=headers):

        parameter_payload = {
        "inputs": """[INST]Your name is Snoop Dogg and you are replying to your homies. Don't repeat your sentences. Keep your replies in a max 5 sentences.
        question: What's up!?
        answer: [/INST]""",
        "parameters" : {
        "max_length": 40,
        }
        }

        res = r.post(url, headers=headers, json=parameter_payload)
        
        return res.status_code

    sent_initial_message = False
    start = time.time()
    elapsed_time = 0
    while (get_status() != 200) and (elapsed_time < 300):
        if st.session_state.verbose:
            # st.session_state.messages.append({"role": "assistant", 
            #                                   "content": 'Initializing Inference Endpoint... Please wait for 1-2 mins.'})
            
            print('Initializing Inference Endpoint... Please wait for 1-2 mins.')
        if not sent_initial_message:
            initial_message()
            sent_initial_message = True
            if st.session_state.verbose:
                # st.session_state.messages.append({"role": "assistant", 
                #                                  "content": 'Initial message sent!'})
                print('Initial message sent!')
                
        time.sleep(90)
        elapsed_time = time.time()-start
    if st.session_state.verbose:
        # st.session_state.messages.append({"role": "assistant", 
        #                                       "content": f'Initialization Complete! Time to Initilize {elapsed_time} secs.'})
        # st.session_state.messages.appe
        st.session_state.messages.append({"role": "assistant", 
                                              "content": f'Initialization Done! Please send your first message to Snoop Dogg.'})
        
        print('Initialization Completed!')
        print('Time Elapsed to Initialize Endpoint', elapsed_time)

    st.session_state['inference_endpoint_initialized'] = True

st.set_page_config(page_title = 'Chat with Snoop Dogg!')

st.title('Chat with Snoop Dogg!')
 
def show_chat_messages():
    for message in st.session_state['messages']:
        with st.chat_message(message['role']):
            st.markdown(message['content'])


def initialize_states():

    if 'messages' not in st.session_state.keys():
        st.session_state['messages'] = []
        st.session_state.messages.append({"role": "assistant", 
                                          "content": 'Hi there! If you wanna chat, please Initialize the session first on the side pane. This ensures that the Hugging Face Inference Endpoint is Initialized.'})

    if 'verbose' not in st.session_state.keys():
        st.session_state['verbose'] = True
    if 'inference_endpoint_initialized' not in st.session_state.keys():
        st.session_state['inference_endpoint_initialized'] = False
   
def main():

    with st.sidebar:
        st.markdown('# Instructions:')
        st.markdown('## 1. Initialize the session')
        st.markdown('Initializing the session / chat may take 1-5 mins. Please be patient. (The time to initialize the endpoint service is dependent on the queue at HuggingFace end. It cannot be controlled.)')
        st.button('Initialize Chat!', on_click=initialize_endpoint, 
                  key='initialize_button', disabled= st.session_state['inference_endpoint_initialized'])
      
        st.markdown('## 2. Start Chat!')

        st.markdown('Note: You are chatting with a Fine Tuned Gemma-2b-it model')

    show_chat_messages()
    
    if question := st.chat_input("Ask a question or Say Something"):
       
        st.session_state.messages.append({"role": "user", "content": question})
        
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message('assistant'):
            response = st.session_state['chain'].invoke(dict(message=question))

            st.markdown(response)
            apth = text_to_speech(response)
            st.audio(apth)

            st.session_state['messages'].append({'role':'assistant', 'content': response})

            
    

if __name__ == '__main__':
    initialize_states()
    load_llm_and_chain()

    main()