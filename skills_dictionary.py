# Skills Dictionary
# Organized by category with synonyms for better matching
# Each skill can have multiple variations (synonyms)

SKILLS_DICTIONARY = {
    # PROGRAMMING LANGUAGES
    "programming_languages": {
        "python": ["python", "py", "python3", "python2"],
        "javascript": ["javascript", "js", "node", "nodejs", "node.js"],
        "java": ["java", "j2ee"],
        "csharp": ["csharp", "c sharp"],
        "go": ["golang"],
        "rust": ["rust"],
        "php": ["php"],
        "ruby": ["ruby", "rails", "ruby on rails"],
        "typescript": ["typescript", "ts"],
        "kotlin": ["kotlin"],
        "swift": ["swift"],
        "r": ["r programming", "r language"],
        "scala": ["scala"],
    },
    
    # WEB FRAMEWORKS & LIBRARIES
    "web_frameworks": {
        "react": ["react", "reactjs", "react.js"],
        "angular": ["angular", "angularjs"],
        "vue": ["vue", "vuejs", "vue.js"],
        "django": ["django"],
        "fastapi": ["fastapi", "fast api"],
        "flask": ["flask"],
        "spring": ["spring", "spring boot"],
        "express": ["express", "expressjs"],
        "nextjs": ["next.js", "nextjs"],
        "nuxt": ["nuxt", "nuxtjs"],
        "laravel": ["laravel"],
        "asp.net": ["asp.net", "aspnet", "asp net"],
    },
    
    # DATABASES & DATA STORAGE
    "databases": {
        "sql": ["sql", "structured query language"],
        "postgresql": ["postgresql", "postgres", "psql"],
        "mysql": ["mysql"],
        "mongodb": ["mongodb", "mongo"],
        "redis": ["redis"],
        "elasticsearch": ["elasticsearch", "elastic search"],
        "dynamodb": ["dynamodb"],
        "cassandra": ["cassandra"],
        "oracle": ["oracle database", "oracle"],
        "sqlite": ["sqlite"],
        "firebase": ["firebase"],
        "mariadb": ["mariadb"],
        "vector_database": ["vector database", "vectordb", "pinecone", "weaviate", "milvus"],
        "knowledge_graph": ["knowledge graph", "knowledge graphs"],
    },
    
    # CLOUD PLATFORMS & DEVOPS
    "cloud_devops": {
        "aws": ["aws", "amazon web services", "amazon aws"],
        "azure": ["azure", "microsoft azure"],
        "gcp": ["gcp", "google cloud", "google cloud platform"],
        "docker": ["docker", "dockerization"],
        "kubernetes": ["kubernetes", "k8s"],
        "terraform": ["terraform"],
        "jenkins": ["jenkins"],
        "gitlab": ["gitlab", "gitlab ci"],
        "github": ["github", "github actions"],
        "circleci": ["circleci", "circle ci"],
        "ansible": ["ansible"],
        "vagrant": ["vagrant"],
        "linux": ["linux"],
        "ubuntu": ["ubuntu"],
    },
    
    # AI / ML / LLM - CORE CONCEPTS
    "ai_ml_core": {
        "artificial_intelligence": ["artificial intelligence", "ai"],
        "machine_learning": ["machine learning", "ml"],
        "deep_learning": ["deep learning"],
        "neural_networks": ["neural networks", "neural network"],
        "llm": ["llm", "large language model", "large language models"],
        "generative_ai": ["generative ai", "generative artificial intelligence", "gen ai", "genai"],
        "nlp": ["nlp", "natural language processing"],
        "computer_vision": ["computer vision", "image processing"],
        "transformers": ["transformers"],
    },
    
    # RAG & RETRIEVAL SYSTEMS
    "rag_retrieval": {
        "rag": ["rag", "retrieval augmented generation"],
        "semantic_search": ["semantic search"],
        "similarity_search": ["similarity search"],
        "information_retrieval": ["information retrieval"],
        "embeddings": ["embeddings", "embedding models", "text embeddings"],
        "vector_search": ["vector search"],
        "document_retrieval": ["document retrieval"],
        "context_retrieval": ["context retrieval"],
    },
    
    # PROMPT ENGINEERING & LLM TECHNIQUES
    "prompt_engineering": {
        "prompt_engineering": ["prompt engineering", "prompt design"],
        "prompt_optimization": ["prompt optimization"],
        "few_shot_learning": ["few shot", "few-shot learning"],
        "zero_shot": ["zero shot", "zero-shot"],
        "in_context_learning": ["in-context learning", "in context learning"],
        "chain_of_thought": ["chain of thought", "chain-of-thought", "cot"],
        "prompt_chaining": ["prompt chaining"],
    },
    
    # AI AGENTS & AUTONOMOUS SYSTEMS
    "ai_agents": {
        "ai_agents": ["ai agents", "ai agent"],
        "autonomous_agents": ["autonomous agents", "autonomous agent"],
        "agent_architecture": ["agent architecture"],
        "agent_orchestration": ["agent orchestration"],
        "tool_use": ["tool use", "tool calling", "function calling"],
        "function_calling": ["function calling"],
        "agent_framework": ["agent framework"],
        "reasoning": ["agentic reasoning"],
        "planning": ["plan generation"],
        "memory": ["memory management", "memory systems"],
    },
    
    # LLM FRAMEWORKS & LIBRARIES
    "llm_frameworks": {
        "langchain": ["langchain"],
        "llamaindex": ["llamaindex", "llama index"],
        "huggingface": ["huggingface", "hugging face"],
        "openai": ["openai", "chatgpt", "gpt"],
        "anthropic": ["anthropic", "claude"],
        "cohere": ["cohere"],
        "replicate": ["replicate"],
        "ollama": ["ollama"],
        "vllm": ["vllm"],
        "transformers": ["transformers", "huggingface transformers"],
    },
    
    # DEEP LEARNING FRAMEWORKS
    "deep_learning": {
        "tensorflow": ["tensorflow"],
        "pytorch": ["pytorch"],
        "keras": ["keras"],
        "jax": ["jax"],
        "flax": ["flax"],
    },
    
    # DATA & ANALYTICS
    "data_analytics": {
        "data_analysis": ["data analysis", "data analytics"],
        "pandas": ["pandas"],
        "numpy": ["numpy"],
        "scikit_learn": ["scikit-learn", "sklearn"],
        "power_bi": ["power bi", "powerbi"],
        "tableau": ["tableau"],
        "looker": ["looker"],
        "qlik": ["qlik"],
        "statistics": ["statistics", "statistical analysis"],
        "sql": ["sql"],
        "data_visualization": ["data visualization"],
        "data_engineering": ["data engineering"],
        "etl": ["etl", "extract transform load"],
        "data_pipeline": ["data pipeline"],
    },
    
    # FINE-TUNING & MODEL TRAINING
    "model_training": {
        "fine_tuning": ["fine tuning", "fine-tuning", "finetuning"],
        "transfer_learning": ["transfer learning"],
        "model_training": ["model training"],
        "supervised_learning": ["supervised learning"],
        "unsupervised_learning": ["unsupervised learning"],
        "reinforcement_learning": ["reinforcement learning", "rl"],
        "rlhf": ["rlhf", "reinforcement learning from human feedback"],
        "hyperparameter_tuning": ["hyperparameter tuning"],
        "model_optimization": ["model optimization"],
    },
    
    # MODEL DEPLOYMENT & INFERENCE
    "model_deployment": {
        "model_deployment": ["model deployment"],
        "inference": ["inference", "model inference"],
        "serving": ["serving", "model serving"],
        "quantization": ["quantization"],
        "distillation": ["distillation", "knowledge distillation"],
        "model_compression": ["model compression"],
        "edge_ai": ["edge ai", "edge inference"],
        "tpu": ["tpu", "tensor processing unit"],
        "gpu": ["gpu", "graphics processing unit"],
    },
    
    # API & WEB STANDARDS
    "api_web": {
        "rest_api": ["rest api", "restful"],
        "graphql": ["graphql"],
        "soap": ["soap"],
        "http": ["http", "https"],
        "json": ["json"],
        "xml": ["xml"],
        "api_design": ["api design"],
        "microservices": ["microservices", "microservice"],
        "websockets": ["websockets", "websocket"],
    },
    
    # VERSION CONTROL & COLLABORATION
    "version_control": {
        "git": ["git"],
        "github": ["github"],
        "gitlab": ["gitlab"],
        "bitbucket": ["bitbucket"],
        "svn": ["svn", "subversion"],
    },
    
    # TESTING & QA
    "testing": {
        "unit_testing": ["unit testing", "unit test"],
        "integration_testing": ["integration testing"],
        "pytest": ["pytest"],
        "jest": ["jest"],
        "mocha": ["mocha"],
        "selenium": ["selenium"],
        "cypress": ["cypress"],
        "test_automation": ["test automation"],
        "qa": ["qa", "quality assurance"],
    },
    
    # MONITORING & OBSERVABILITY
    "monitoring": {
        "monitoring": ["monitoring"],
        "logging": ["logging"],
        "debugging": ["debugging"],
        "observability": ["observability"],
        "prometheus": ["prometheus"],
        "grafana": ["grafana"],
        "datadog": ["datadog"],
        "new_relic": ["new relic"],
    },
    
    # SOFT SKILLS
    "soft_skills": {
        "communication": ["communication", "communication skills", "communicating"],
        "leadership": ["leadership", "leading", "lead team", "team leadership"],
        "problem_solving": ["problem solving", "problem-solving"],
        "critical_thinking": ["critical thinking"],
        "teamwork": ["teamwork", "team collaboration", "team player"],
        "collaboration": ["collaboration", "collaborating"],
        "time_management": ["time management"],
        "adaptability": ["adaptability", "adaptive", "flexible"],
        "creativity": ["creativity", "creative thinking"],
        "attention_to_detail": ["attention to detail"],
        "interpersonal": ["interpersonal skills"],
        "presentation": ["presentation", "presentation skills", "public speaking"],
        "negotiation": ["negotiation", "negotiating"],
        "mentoring": ["mentoring", "mentor"],
        "analytical_skills": ["analytical skills", "analytical thinking"],
    },
    
    # PROJECT MANAGEMENT & AGILE
    "project_management": {
        "agile": ["agile", "agile methodology"],
        "scrum": ["scrum", "scrum master"],
        "kanban": ["kanban"],
        "jira": ["jira"],
        "project_management": ["project management"],
        "stakeholder_management": ["stakeholder management"],
        "sprint": ["sprint", "sprints"],
    },
    
    # BUSINESS & PRODUCT
    "business": {
        "product_management": ["product management", "product manager"],
        "business_analysis": ["business analysis", "business analyst"],
        "business_intelligence": ["business intelligence", "bi"],
        "requirements_gathering": ["requirements gathering"],
        "roadmap": ["roadmap planning", "roadmap"],
        "market_research": ["market research"],
        "stakeholder_management": ["stakeholder management"],
        "sales": ["sales", "selling"],
        "marketing": ["marketing"],
        "strategy": ["strategy", "strategic planning"],
        "finance": ["finance", "financial analysis"],
        "accounting": ["accounting"],
    },
           # MICROSOFT BUSINESS PLATFORM
       "microsoft_platform": {
           "dynamics_365": ["dynamics 365", "d365", "microsoft dynamics"],
           "power_automate": ["power automate"],
           "copilot_studio": ["copilot studio"],
           "microsoft_fabric": ["microsoft fabric"],
           "azure_devops": ["azure devops"],
           "sharepoint": ["sharepoint"],
       },
       
       # DESIGN
    "design": {
        "ui_ux": ["ui/ux", "ux design", "ui design"],
        "figma": ["figma"],
        "adobe_xd": ["adobe xd", "xd"],
        "sketch": ["sketch"],
        "web_design": ["web design"],
        "graphic_design": ["graphic design"],
        "user_experience": ["user experience", "ux"],
        "user_interface": ["user interface", "ui"],
        "wireframing": ["wireframing"],
        "prototyping": ["prototyping"],
    },
    
    # SECURITY & COMPLIANCE
    "security": {
        "cybersecurity": ["cybersecurity", "cyber security"],
        "network_security": ["network security"],
        "data_security": ["data security"],
        "encryption": ["encryption"],
        "authentication": ["authentication"],
        "authorization": ["authorization"],
        "oauth": ["oauth"],
        "gdpr": ["gdpr"],
        "compliance": ["compliance"],
    },
    
    # INFRASTRUCTURE & SYSTEMS
    "infrastructure": {
        "system_design": ["system design"],
        "scalability": ["scalability", "scalable"],
        "load_balancing": ["load balancing"],
        "caching": ["caching"],
        "cdn": ["cdn", "content delivery network"],
        "monitoring": ["monitoring", "observability"],
        "logging": ["logging"],
        "debugging": ["debugging"],
    },
    
    # MOBILE DEVELOPMENT
    "mobile": {
        "ios": ["ios", "iphone"],
        "android": ["android"],
        "react_native": ["react native"],
        "flutter": ["flutter"],
        "swift": ["swift"],
        "kotlin": ["kotlin"],
        "xamarin": ["xamarin"],
        "mobile_development": ["mobile development"],
    },
    
    # CONTENT MANAGEMENT
    "cms": {
        "wordpress": ["wordpress"],
        "drupal": ["drupal"],
        "joomla": ["joomla"],
        "content_management": ["content management system", "cms"],
    },
    
    # DOCUMENTATION & COMMUNICATION
    "documentation": {
        "documentation": ["documentation", "technical writing"],
        "markdown": ["markdown"],
        "api_documentation": ["api documentation"],
    },
    
    # GENERAL TECHNICAL TERMS
    "general": {
        "coding": ["coding", "programming", "development"],
        "debugging": ["debugging"],
        "optimization": ["optimization", "optimizing"],
        "performance": ["performance tuning", "performance"],
        "architecture": ["architecture", "software architecture"],
    },
}

# Flatten dictionary for easy skill lookup
# This creates a mapping of all synonyms to their canonical skill name
SKILL_SYNONYMS = {}
for category, skills in SKILLS_DICTIONARY.items():
    for skill_name, synonyms in skills.items():
        for synonym in synonyms:
            SKILL_SYNONYMS[synonym.lower()] = skill_name

# Get all unique skills (for matching)
ALL_SKILLS = set(SKILL_SYNONYMS.keys())

def get_skill_category(skill):
    """Get the category of a skill"""
    skill_lower = skill.lower()
    if skill_lower in SKILL_SYNONYMS:
        skill_name = SKILL_SYNONYMS[skill_lower]
        for category, skills in SKILLS_DICTIONARY.items():
            if skill_name in skills:
                return category
    return None

def normalize_skill_name(skill):
    """Convert a synonym to the canonical skill name"""
    skill_lower = skill.lower()
    if skill_lower in SKILL_SYNONYMS:
        return SKILL_SYNONYMS[skill_lower]
    return skill_lower

def get_all_skills_in_category(category):
    """Get all skills in a specific category"""
    if category in SKILLS_DICTIONARY:
        return list(SKILLS_DICTIONARY[category].keys())
    return []

def get_all_categories():
    """Get all skill categories"""
    return list(SKILLS_DICTIONARY.keys())

# Friendly category names for display
CATEGORY_DISPLAY_NAMES = {
    "programming_languages": "📘 Programming Languages",
    "web_frameworks": "🌐 Web Frameworks",
    "databases": "🗄️ Databases & Storage",
    "cloud_devops": "☁️ Cloud & DevOps",
    "ai_ml_core": "🤖 AI/ML Core Concepts",
    "rag_retrieval": "📚 RAG & Retrieval Systems",
    "prompt_engineering": "✍️ Prompt Engineering",
    "ai_agents": "🎯 AI Agents & Autonomous Systems",
    "llm_frameworks": "⚙️ LLM Frameworks",
    "deep_learning": "🧠 Deep Learning Frameworks",
    "data_analytics": "📊 Data & Analytics",
    "model_training": "🏋️ Model Training",
    "model_deployment": "🚀 Model Deployment & Inference",
    "api_web": "🔌 API & Web Standards",
    "version_control": "📝 Version Control",
    "testing": "✅ Testing & QA",
    "monitoring": "📡 Monitoring & Observability",
    "soft_skills": "💼 Soft Skills",
    "project_management": "📋 Project Management",
    "business": "💰 Business & Product",
    "design": "🎨 Design",
    "security": "🔒 Security & Compliance",
    "infrastructure": "🏗️ Infrastructure & Systems",
    "mobile": "📱 Mobile Development",
    "cms": "📄 Content Management",
    "documentation": "📖 Documentation",
    "general": "⚙️ General Technical",
}
