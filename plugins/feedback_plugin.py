import logging
import json
from typing import Annotated
from semantic_kernel.functions import kernel_function
from services.redis_service import redis_client

logger = logging.getLogger(__name__)

class FeedbackPlugin:
    """
    The Feedback Agent's Logic.
    Responsible for validating and storing user feedback.
    """

    @kernel_function(
        description="Stores user feedback or corrections regarding specific product data."
    )
    def store_feedback(
        self, 
        designation: Annotated[str, "The product designation related to the feedback"],
        attribute: Annotated[str, "The attribute being corrected or commented on"],
        feedback_note: Annotated[str, "The actual correction or feedback text"]
    ) -> str:
        logger.info(f"Feedback Agent: Triggered for {designation}")
        
        if not redis_client.client:
            logger.warning("Feedback Agent: Redis unavailable, cannot store feedback.")
            return "Feedback received, but storage is unavailable."

        # Store in a list in Redis
        key = "feedback:submissions"
        payload = json.dumps({
            "designation": designation,
            "attribute": attribute,
            "note": feedback_note,
            "timestamp": "now" 
        })
        
        redis_client.rpush(key, payload)
        logger.info(f"Feedback Agent: Feedback persisted to Redis key '{key}'.")
        return f"Feedback securely stored for {designation} ({attribute})."