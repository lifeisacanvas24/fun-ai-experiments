# AI Git Commit Message Generator

An intelligent Python script that generates commit messages using AI models. This tool streamlines your Git workflow by suggesting contextually relevant commit messages based on your staged changes.

## 🚀 Features

- 🧠 Uses OpenAI's GPT models and Google's Gemini model
- 🔄 Supports multiple AI models (GPT-3.5, GPT-4, Gemini)
- 📊 Generates multiple commit message suggestions
- 🖥️ Interactive CLI for selecting or customizing commit messages
- 🔒 Secure API key management
- 📝 Logging for requests and responses

## 📋 Prerequisites

- Python 3.6+
- Git
- API keys for OpenAI and/or Google Gemini

## 📦 Installation and Dependency Management

### Initial Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/ai-git-commit-message.git
   ```

   cd ai-git-commit-message

   # On Windows

   python -m venv venv
   .\venv\Scripts\activate

   # On macOS/Linux

   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip list
   pip install package_name
   pip freeze > requirements.txt
   pip install --upgrade -r requirements.txt
   pip list --outdated
   pip install requests
   pip install --upgrade requests
   pip freeze > requirements.txt
   requests>=2.31.0
   python-dotenv>=1.0.0 # (optional, for future env file support)

   ## 🔑 API Key Setup

   ### Google Gemini API (Free)

   1. Go to the [Google AI Studio](https://makersuite.google.com/app/apikey).
   2. Sign in with your Google account.
   3. Click on "Create API Key" to generate a new API key.
   4. Save the API key in `~/.ssh/gemini-api-key`.

   ### OpenAI API (Paid)

   1. Sign up for an OpenAI account at [OpenAI](https://openai.com/).
   2. Navigate to the API section and create a new API key.
   3. Save the API key in `~/.ssh/openai-api-key`.

   **Note**: OpenAI's API is a paid service. Ensure you understand their pricing before using it.

   ## 🖥️ Usage

   Run the script in your Git repository:

   Follow the prompts to select or customize your commit message.

   ## 🔮 Future Plans

   We're constantly working to improve and expand this tool. Here are some features we're planning to add:

   1. Integration with more Git operations (e.g., pull requests, merge commit messages)
   2. Support for additional free and paid AI tools
   3. Customizable commit message templates
   4. Integration with popular Git GUIs and IDEs

   ## 🤝 Contributing

   Contributions are welcome! Please feel free to submit a Pull Request.

   ## 📄 License

   This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

   ## 🙏 Acknowledgements

   - OpenAI for their GPT models
   - Google for the Gemini API
   - All contributors and users of this project
