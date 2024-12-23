# AI Model Configuration
AI_CONFIG = {
	'html_analyzer': {
		'model': 'gemini-exp-1206',  # Using Gemini Pro for HTML analysis
		'generation_config': {
			'temperature': 1,
			'top_p': 0.95,              # No nucleus sampling
			'top_k': 40,             # Standard setting
			'max_output_tokens': 8192,  # Maximum output length
		}
	},
	'code_generator': {
		'model': 'gemini-exp-1206',  # Using Gemini Pro for code generation
		'generation_config': {
			'temperature': 0.0001,     # Very low temperature for deterministic code
			'top_p': 1,              # No nucleus sampling
			'top_k': 40,             # Standard setting
			'max_output_tokens': 8192,  # Maximum output length
		}
	}
}

# Prompt Templates
PROMPTS = {
	'html_analysis': '''
	You are a specialized HTML analyzer. Your task is to extract and identify relevant tags and elements from the provided HTML content.
	
	URL: {url}
	Target Description: {target_description}
	
	HTML Content:
	{html}
	
	Provide a structured JSON output containing:
	1. Relevant HTML tags and their attributes
	2. CSS selectors for target elements
	3. Data structure patterns found
	
	Format your response as valid JSON only.
	'''.strip(),
	
	'code_generation': '''
	You are a Python code generator. Based on the following HTML analysis results, generate clean, production-ready Python code.
	
	Analysis Results:
	{analysis_results}
	
	Requirements:
	- Use BeautifulSoup4 for parsing
	- Include proper error handling
	- Include logging
	- Return structured data
	
	Generate only valid Python code without any explanatory text or markdown formatting.
	'''.strip()
}