# Create a comprehensive configuration management system
# Include API keys, model settings, database paths, caching configs
# Support environment variables and YAML config files

import os
from dataclasses import dataclass
from typing import Dict, Any
import yaml

@dataclass
class AgentConfig:
    """Agent configuration for behavior and integration patterns"""
    integration_mode: str = "direct"  # "direct" or "tools"
    enable_tool_calling: bool = False
    max_tool_calls: int = 5

@dataclass
class APIConfig:
    """API configuration for external services"""
    openai_api_key: str
    alpha_vantage_key: str
    openai_model: str = "gpt-4"
    max_tokens: int = 1000
    temperature: float = 0.7

@dataclass
class VectorDBConfig:
    """Vector database configuration for FAISS"""
    index_path: str = "data/faiss_index"
    embedding_model: str = "text-embedding-ada-002"
    chunk_size: int = 500
    chunk_overlap: int = 50

@dataclass
class CacheConfig:
    """Caching configuration for market data"""
    market_data_ttl: int = 1800  # 30 minutes
    portfolio_cache_ttl: int = 300  # 5 minutes
    max_cache_size: int = 1000

@dataclass
class AppConfig:
    """Main application configuration"""
    api: APIConfig
    vector_db: VectorDBConfig
    cache: CacheConfig
    agents: Dict[str, AgentConfig]
    debug: bool = False
    log_level: str = "INFO"
    show_workflow_status: bool = False

def load_config() -> AppConfig:
    """Load configuration from environment variables and config file"""
    # Load from environment variables first
    api_config = APIConfig(
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        alpha_vantage_key=os.getenv("ALPHA_VANTAGE_API_KEY", ""),
        openai_model=os.getenv("MODEL_NAME", "gpt-4"),
        max_tokens=int(os.getenv("MAX_TOKENS", "1000")),
        temperature=float(os.getenv("TEMPERATURE", "0.7"))
    )
    
    # Default configurations
    vector_db_config = VectorDBConfig()
    cache_config = CacheConfig()
    
    # Default agent configurations
    default_agents = {
        "market_agent": AgentConfig(
            integration_mode="tools",  # Default to tool calling for learning
            enable_tool_calling=True,
            max_tool_calls=5
        ),
        "portfolio_agent": AgentConfig(integration_mode="direct"),
        "goal_agent": AgentConfig(integration_mode="direct")
    }
    
    # Try to load from YAML config file
    config_path = "config.yaml"
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                yaml_config = yaml.safe_load(f)
            
            # Update API config from YAML
            if 'apis' in yaml_config:
                api_section = yaml_config['apis']
                if 'openai' in api_section:
                    openai_config = api_section['openai']
                    api_config.openai_model = openai_config.get('model', api_config.openai_model)
                    api_config.max_tokens = openai_config.get('max_tokens', api_config.max_tokens)
                    api_config.temperature = openai_config.get('temperature', api_config.temperature)
            
            # Update agent configs from YAML
            if 'agents' in yaml_config:
                for agent_name, agent_yaml_config in yaml_config['agents'].items():
                    if agent_name in default_agents:
                        default_agents[agent_name].integration_mode = agent_yaml_config.get(
                            'integration_mode', 
                            default_agents[agent_name].integration_mode
                        )
                        default_agents[agent_name].enable_tool_calling = agent_yaml_config.get(
                            'enable_tool_calling', 
                            default_agents[agent_name].enable_tool_calling
                        )
                        default_agents[agent_name].max_tool_calls = agent_yaml_config.get(
                            'max_tool_calls', 
                            default_agents[agent_name].max_tool_calls
                        )
            
        except Exception as e:
            print(f"Warning: Could not load config.yaml: {e}")
    
    return AppConfig(
        api=api_config,
        vector_db=vector_db_config,
        cache=cache_config,
        agents=default_agents,
        debug=os.getenv("DEBUG", "False").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", "INFO")
    )