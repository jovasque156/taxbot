import streamlit as st
from langchain.agents import initialize_agent, AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import StreamlitChatMessageHistory
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from langchain.tools import Tool
from tools import tools
from langchain.chains import LLMMathChain

system_message='''Eres un chatbot muy amable teniendo una conversación con un humano. Solo sabes calcular impuestos de Chile, por tanto SIEMPRE haz los cálculos en CLP (Pesos Chilenos). SOLO respondes a preguntas relacionadas con cálculo de impuestos. Ante cualquier pregunta NO RELACIONADA con impuestos, debes indicar que no puedes responder a esa pregunta.
Para responder las preguntas tienes acceso a las siguientes herramientas:

Calculo Impuesto: útil para calcular el impuesto dado el INGRESO ANUAL y el AÑO FISCAL. Formato input función (ingreso_anual,año). Solo años 2021, 2022, y 2023.
Calculadora: util para cuando neceistas responder preguntas sobre matemáticas

Use the following format:
Question: the input question you must answer
Thought: you should always think about what to do, skip to Final Answer if you think no action is needed.
Action: the action to take, should be one of [Calculo Impuesto, Calculadora, Final Answer]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Chat history:
{chat_history}

Question: {input}
Thought:{agent_scratchpad}'''
msgs = StreamlitChatMessageHistory()
memory = ConversationBufferMemory(
    chat_memory=msgs, return_messages=True, memory_key="chat_history", output_key="output"
)



st.session_state.disabled = False

with st.sidebar:
    if ('OPENAI_API_KEY' in st.secrets) and ('openai_model' in st.secrets):
        api_key = st.secrets['OPENAI_API_KEY']
        id_model = st.secrets['openai_model']
    else:    
        api_key = st.text_input("OpenAI API Key", placeholder='Ingresa tu OPEN API Key', type="password", disabled=st.session_state.disabled)
        id_model = st.selectbox('Modelo', ('gpt-3.5-turbo', 'gpt-4'), index=None, placeholder='Selecciona un modelo', disabled=st.session_state.disabled)
    
    placeholder = st.empty()    
    with placeholder.container():
        if not api_key or not id_model:
            st.warning('Por favor, ingresa tus credenciales y selecciona el modelo!', icon='⚠️')
        else:
            st.session_state.disabled = True
            st.success('¡API KEY ingresada! \n\nYa puedes ingresar los mensajes. \n\n Para seleccionar otro modelo, refresca la página', icon='👉')

st.title("🔎 TaxBot")

if len(msgs.messages) == 0 or st.sidebar.button("Reset chat history"):
    msgs.clear()
    st.session_state.steps = {}

avatars = {"human": "user", "ai": "assistant"}

for idx, msg in enumerate(msgs.messages):
    with st.chat_message(avatars[msg.type]):
        for step in st.session_state.steps.get(str(idx), []):
            if step[0].tool == "_Exception":
                continue
            with st.status(f"**{step[0].tool}**: {step[0].tool_input}", state="complete"):
                st.write(step[0].log)
                st.write(step[1])
        st.write(msg.content)

st.write('Este es un chatbot de prueba para trabajar en relación al cálculo de impuestos en Chile. Por favor, ingresa tu pregunta en la casilla de más abajo.')
if prompt := st.chat_input(placeholder='Escribe tu pregunta aquí'):
    st.chat_message("user").write(prompt)

    if not api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    llm_m = OpenAI(temperature=0, model_name="gpt-3.5-turbo", openai_api_key=api_key, streaming=True)
    llm_math_chain = LLMMathChain.from_llm(llm_m)
    tools = tools + [Tool(
            name="Calculadora",
            func=llm_math_chain.run,
            description="Util para cuando neceistas responder preguntas sobre matemáticas",
        )]

    descripcion_tools = ''
    for t in tools:
        descripcion_tools += '>'+t.name+':'+t.description+'\n'

    llm = ChatOpenAI(temperature=0.2,model_name=id_model, streaming=True)
    tax_agent = initialize_agent(tools=tools,
                            llm=llm, 
                            memory=memory,
                            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, 
                            handle_parsing_errors=True,
                            return_intermediate_steps=True)
    
    tax_agent.agent.llm_chain.prompt.input_variables = ['chat_history', 'input', 'agent_scratchpad']
    tax_agent.agent.llm_chain.prompt.template = system_message

    with st.chat_message("assistant"):
        st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=True)
        response = tax_agent(prompt, callbacks=[st_cb])
        # tax_agent.early_stopping_method()
        st.write(response["output"])
        # st.write(response)
        st.session_state.steps[str(len(msgs.messages) - 1)] = response["intermediate_steps"]