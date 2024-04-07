
from typing import Any, Dict, List, Mapping, Optional
from pydantic import Extra, root_validator

from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM
from langchain.llms.utils import enforce_stop_tokens

from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import requests as r

load_dotenv()
# import torch
# from peft import PeftModel, PeftConfig
# from transformers import AutoModelForCausalLM, AutoTokenizer

class HuggingInferenceEndpointLLM(LLM):

    temperature: Any
    repetition_penalty: Any
    max_new_tokens: Any
    hf_model_or_api_url: Any
    hf_token: Any
    client: Any
   
    class Config:
        """Confguration for the pydantic obje|ct."""
        extra = Extra.forbid

    def __init__(self, hf_model_or_api_url, hf_token, temperature=0.8, 
                 repetition_penalty=1.1, max_new_tokens=1000, 
                 verbose=True, **kwargs):
        super().__init__(**kwargs)

        self.temperature = temperature
        self.repetition_penalty = repetition_penalty
        self.max_new_tokens = max_new_tokens
        self.hf_model_or_api_url = hf_model_or_api_url
        self.hf_token = hf_token
        self.client = InferenceClient(model=hf_model_or_api_url, 
                                      token=hf_token)
        self.verbose = verbose
        

        # model, tokenizer = load_ft_model_from_hf()
        # self.hf_model = model
        # self.hf_tokenizer = tokenizer

    @property
    def _llm_type(self) -> str:
        return "huggingface_inference_endpoint"
    
  
    def get_status(self):
        headers = {"Authorization": f"Bearer {self.hf_token}",
            "Content-Type": "application/json"}
        res = r.get(self.hf_model_or_api_url, headers=headers)

        return res.status_code



    def send_initial_message(self):

        parameter_payload = {
        "inputs": """[INST]Your name is Snoop Dogg and you are replying to your homies. Don't repeat your sentences. Keep your replies in a max 5 sentences.
        question: What's up!?
        answer: [/INST]""",
        "parameters" : {
        "max_length": 40,
        }
        }

        headers = {"Authorization": f"Bearer {self.hf_token}",
                "Content-Type": "application/json"}

        res = r.post(self.hf_model_or_api_url, headers=headers, json=parameter_payload)
        
        return res.status_code
  
    def initialize(self):

        import time

        sent_initial_message = False

        start = time.time()
        elapsed_time = 0
        while (self.get_status() != 200) and (elapsed_time < 300):
            if self.verbose:
                print('Initializing Inference Endpoint... Please wait for 1-2 mins.')
            if not sent_initial_message:
                self.send_initial_message()
                sent_initial_message = True
                if self.verbose:
                    print('Initial message sent!')
            time.sleep(90)
            elapsed_time = time.time()-start
        if self.verbose:
            print('Initialization Completed!')
            print('Time Elapsed to Initialize Endpoint', time.time()-start)

    
    def _call(self, prompt, stop: Optional[List[str]] = None, run_manager: Optional[CallbackManagerForLLMRun] = None,):
        
        # print(prompt)
        text = self.client.text_generation(prompt, 
                               max_new_tokens=self.max_new_tokens,
                               temperature=self.temperature,
                               repetition_penalty=self.repetition_penalty)
        

        if stop is not None:
            text = enforce_stop_tokens(text, stop)
        # print(text)
        return text

