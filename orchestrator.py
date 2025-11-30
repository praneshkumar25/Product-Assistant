import json
import logging
import asyncio

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion, AzureChatPromptExecutionSettings
from semantic_kernel.contents import ChatHistory
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior

from config import Config
from services.redis_service import redis_client
from plugins.datasheet_plugin import DatasheetPlugin
from plugins.feedback_plugin import FeedbackPlugin

logger = logging.getLogger(__name__)

class Orchestrator:
    def __init__(self):
        self.kernel = None

    def _initialize_kernel(self):
        """Lazy initialization of the kernel."""
        if self.kernel:
            return self.kernel

        kernel = Kernel()
        
        # Add Azure OpenAI Service
        kernel.add_service(
            AzureChatCompletion(
                service_id="chat-gpt",
                deployment_name=Config.AZURE_OPENAI_DEPLOYMENT_NAME,
                endpoint=Config.AZURE_OPENAI_ENDPOINT,
                api_key=Config.AZURE_OPENAI_API_KEY,
            )
        )

        # Register Plugins (Agents)
        kernel.add_plugin(DatasheetPlugin(), plugin_name="DatasheetPlugin")
        kernel.add_plugin(FeedbackPlugin(), plugin_name="FeedbackPlugin")
        
        self.kernel = kernel
        return self.kernel

    async def process_chat(self, message: str, session_id: str) -> str:
        logger.info(f"Orchestrator: Processing message for session '{session_id}'")
        kernel = self._initialize_kernel()
        
        # Restore State (Chat History) from Redis
        history_key = f"chat:history:{session_id}"
        chat_history = ChatHistory()
        
        system_prompt = (
            "You are a specialized industrial assistant. "
            "Your role is to route user requests to the correct tool: "
            "1. If the user asks for product data (dimensions, specs, descriptions), use DatasheetPlugin. "
            "2. If the user provides corrections or feedback, use FeedbackPlugin. "
            "RULES: "
            "- NEVER invent values. If the tool returns 'Not Found', state that clearly. "
            "- Be concise. "
            "- Use the conversation history to resolve pronouns (e.g., 'its width' refers to the previous product)."
        )
        chat_history.add_system_message(system_prompt)

        stored_history = redis_client.lrange(history_key, 0, -1)
        for item in stored_history:
            try:
                msg_obj = json.loads(item)
                if msg_obj['role'] == 'user':
                    chat_history.add_user_message(msg_obj['content'])
                elif msg_obj['role'] == 'assistant':
                    chat_history.add_assistant_message(msg_obj['content'])
            except json.JSONDecodeError:
                pass
        
        # Add current message
        chat_history.add_user_message(message)

        # Invoke Kernel with Auto Function Calling
        chat_completion = kernel.get_service(service_id="chat-gpt")
        
        execution_settings = AzureChatPromptExecutionSettings(
            service_id="chat-gpt",
            function_choice_behavior=FunctionChoiceBehavior.Auto()
        )

        try:
            response = await chat_completion.get_chat_message_content(
                chat_history=chat_history,
                settings=execution_settings,
                kernel=kernel
            )
            
            reply_text = str(response)
            logger.info(f"Orchestrator: Response generated: {reply_text[:50]}...")

            # Save State (Update Redis)
            redis_client.rpush(history_key, json.dumps({"role": "user", "content": message}))
            redis_client.rpush(history_key, json.dumps({"role": "assistant", "content": reply_text}))
            redis_client.expire(history_key, 3600)

            return reply_text

        except Exception as e:
            logger.error(f"Orchestrator: Error in processing: {e}")
            return "I encountered an error processing your request."

# Singleton instance
orchestrator = Orchestrator()