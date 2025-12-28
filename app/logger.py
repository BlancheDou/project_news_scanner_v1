"""Custom logging setup for the application."""
import logging
import sys

def setup_logger(name: str = "market_monitor") -> logging.Logger:
    """Set up a logger with custom formatting."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

def log_agent_decision(logger: logging.Logger, tool_name: str):
    """Log agent decision to call a tool."""
    logger.info(f"[Agent] Decided to call tool: {tool_name}")

def log_system_output(logger: logging.Logger, output: str):
    """Log system tool output."""
    logger.info(f"[System] Tool Output: '{output}'")

def log_agent_answer(logger: logging.Logger, answer: str):
    """Log agent final answer."""
    logger.info(f"[Agent] Final Answer: '{answer}'")

