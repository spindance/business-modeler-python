from typing import Any, Dict

# from langchain.callbacks import get_openai_callback
from langchain.callbacks.base import BaseCallbackHandler
from langchain.chains import LLMChain, SequentialChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

from utils import extract_variable_names


class Engine:
    def __init__(
        self, api_key, prompt_list, callback_handler, verbose, model_name, temperature
    ):
        self.api_key = api_key
        self.prompt_list = prompt_list
        self.callback_handler = callback_handler
        self.verbose = verbose
        self.model_name = model_name
        self.temperature = temperature

    def run(self, seed):
        chain = self.build_chain(
            self.api_key,
            self.prompt_list,
            self.callback_handler,
            verbose=self.verbose,
            model_name=self.model_name,
            temperature=self.temperature,
        )
        return chain({"seed": seed})

    def create_llm_chain(self, llm, prompt_text, output_key, callback_func):
        monitor = CallbackHandler(callback_func)
        input_keys = extract_variable_names(prompt_text)

        return LLMChain(
            llm=llm,
            prompt=PromptTemplate(input_variables=input_keys, template=prompt_text),
            output_key=output_key,
            callbacks=[monitor],
            tags=[output_key],
        )

    def build_chain(
        self,
        api_key,
        prompts_list,
        callback_func,
        verbose=False,
        model_name="gpt-3.5-turbo-16k",
        temperature=0.7,
    ):
        # Initialize ChatOpenAI
        llm = ChatOpenAI(
            openai_api_key=api_key, model=model_name, temperature=temperature
        )

        # Chains created using the create_llm_chain function
        chains = [
            self.create_llm_chain(
                llm,
                prompt["template"],
                prompt["output"],
                callback_func,
            )
            for prompt in prompts_list
        ]

        # Calculate input_variables and output_variables
        input_variables = extract_variable_names(prompts_list[0]["template"])

        output_variables = [prompt["output"] for prompt in prompts_list]

        # Sequential chain
        sequential_chain = SequentialChain(
            chains=chains,
            input_variables=input_variables,
            output_variables=output_variables,
            verbose=verbose,
        )

        return sequential_chain


class CallbackHandler(BaseCallbackHandler):
    """
    Custom callback handler class for monitoring the progress of the chains.

    This class is a subclass of BaseCallbackHandler and is used to output
    progress information when a chain starts executing.

    Attributes:
        None
    """

    def __init__(self, callback_func):
        self.callback_func = callback_func

    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> Any:
        """
        Callback function that is executed when a chain starts.

        Parameters:
        - serialized (dict): The serialized chain information.
        - inputs (dict): The inputs passed to the chain.
        - kwargs (dict): Additional keyword arguments containing tags.

        Returns:
        - None
        """
        self.callback_func(serialized, inputs, **kwargs)
