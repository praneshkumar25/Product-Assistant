import logging
from typing import Annotated
from semantic_kernel.functions import kernel_function
from services.redis_service import redis_client
from services.data_manager import data_manager

logger = logging.getLogger(__name__)

class DatasheetPlugin:
    """
    The Q&A Agent's Logic.
    Responsible for retrieving product data from Cache or Files.
    """
    
    @kernel_function(
        description="Retrieves specific technical attributes (width, diameter, weight, description, etc.) for a product designation from the datasheet."
    )
    def get_product_attribute(
        self, 
        designation: Annotated[str, "The product code or designation (e.g., 6205)"], 
        attribute: Annotated[str, "The specific attribute requested (e.g., width, limiting speed, description)"]
    ) -> str:
        logger.info(f"Q&A Agent: Triggered for Product='{designation}', Attribute='{attribute}'")
        
        # 1. Check Cache (Redis)
        cache_key = f"cache:product:{designation}:{attribute}"
        cached_val = redis_client.get(cache_key)
        
        if cached_val:
            logger.info(f"Q&A Agent: Cache HIT for {cache_key}")
            return f"[Cached] {cached_val}"

        logger.info(f"Q&A Agent: Cache MISS for {cache_key}")

        # 2. Check Data Source (Files)
        val = data_manager.find_attribute(designation, attribute)
        
        if val:
            # Write to cache (1 hour expiry)
            redis_client.setex(cache_key, 3600, val)
            logger.info(f"Q&A Agent: Stored value in cache for {cache_key}")
            return val
        
        return "Not Found"