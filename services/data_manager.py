import os
import glob
import json
import logging
from config import Config

logger = logging.getLogger(__name__)

class DataManager:
    """Helper to read local JSON files from the 'data' directory."""
    def __init__(self):
        self.data_store = []
        self.load_data()

    def load_data(self):
        """Loads all JSON files from the configured data directory."""
        logger.info("DataManager: Starting to load data files...")
        files = glob.glob(Config.DATA_DIR)
        
        if not files:
            logger.warning(f"DataManager: No JSON files found in {Config.DATA_DIR}")
            return

        loaded_count = 0
        for file_path in files:
            try:
                logger.info(f"DataManager: Reading file: {file_path}")
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                    
                    if isinstance(content, list):
                        self.data_store.extend(content)
                        loaded_count += len(content)
                    elif isinstance(content, dict):
                        self.data_store.append(content)
                        loaded_count += 1
            except Exception as e:
                logger.error(f"DataManager: Error reading {file_path}: {e}")
        
        logger.info(f"DataManager: Load complete. Total items stored: {len(self.data_store)}")

    def find_attribute(self, designation: str, attribute: str) -> str:
        """
        Searches in memory data using the complex schema.
        Searches: top-level keys, dimensions, properties, performance, logistics, specifications.
        """
        designation_clean = designation.strip().lower()
        attribute_clean = attribute.strip().lower()

        logger.info(f"DataManager: Searching for Designation='{designation_clean}', Attribute='{attribute_clean}'")
        
        # Finding the specific product object
        target_product = None
        for item in self.data_store:
            if str(item.get('designation', '')).lower() == designation_clean:
                target_product = item
                break
        
        if not target_product:
            logger.info(f"DataManager: Designation '{designation}' not found in data store.")
            return None

        # Search for the attribute within the found product
        # Top-Level Keys
        for key, value in target_product.items():
            if attribute_clean in key.lower():
                return str(value)

        # Checking Nested Lists
        nested_categories = ['dimensions', 'properties', 'performance', 'logistics', 'specifications']
        for category in nested_categories:
            if category in target_product and isinstance(target_product[category], list):
                for param in target_product[category]:
                    param_name = param.get('name', '').lower()
                    if attribute_clean in param_name:
                        value = param.get('value')
                        unit = param.get('unit', '')
                        return f"{value} {unit}".strip()

        logger.info(f"DataManager: Attribute '{attribute}' not found for product '{designation}'.")
        return None

# Singleton instance
data_manager = DataManager()