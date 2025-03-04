# Advanced Programming for Data Science - Project 1

This project analyzes movie data from the CMU movie corpus, featuring interactive visualizations and AI-powered genre classification using Streamlit.

## 1. Install Dependencies

All required Python packages are listed in `requirements.txt`. Install them using pip:
```bash
pip install -r requirements.txt
```

## 2. Create and Activate a Virtual Environment

It's highly recommended to use a virtual environment to manage project dependencies in isolation.

### macOS/Linux:
Create the virtual environment:
```bash
python3 -m venv venv  # Or python -m venv venv if python3 is not your default
```

Activate the virtual environment:
```bash
source venv/bin/activate
```

### Windows:
Create the virtual environment:
```bash
python -m venv venv
```

Activate the virtual environment:
```bash
venv\Scripts\activate
```

After activating, the virtual environment name (e.g., `(venv)`) should appear in your terminal prompt.

## 3. Set Up Ollama for Genre Classification

The genre classification feature requires Ollama, a local LLM server:

1. Install Ollama from [https://ollama.ai](https://ollama.ai)

2. Pull the Mistral model (one-time setup):
```bash
ollama pull mistral
```

3. Start the Ollama server:
```bash
ollama serve
```

**Note**: Keep the Ollama server running in a separate terminal window while using the app. The server needs to be active for the genre classification to work.

## 4. Run Tests

This project uses pytest for testing. Ensure your virtual environment is activated, navigate to the project's root directory, and run:
```bash
pytest
```

### Test Discovery:
- `pytest` automatically discovers test files (usually named `test_*.py` or `*_test.py`) and test functions (usually named `test_*`).
- Running specific tests:
```bash
pytest test_app.py  # Run all tests in test_app.py
pytest test_app.py::test_function_name  # Run a specific test function
```

### Test Output:
`pytest` provides detailed test results, including any failures or errors.

### Coverage (Optional):
If you have `pytest-cov` installed (`pip install pytest-cov`), you can generate coverage reports:
```bash
pytest --cov=./your_module_name  # Replace with the name of your module
```

## 5. Run the Streamlit App

To start the Streamlit application, ensure your virtual environment is activated and run:
```bash
streamlit run app.py
```

This will launch the Streamlit app in your default web browser. **The app automatically checks if the necessary data is in the /data folder. If not, it will download the data from the internet (src/__init__.py).**

## 6. Using the App

The app has three main sections:

1. **Main Dashboard**: View movie types, actor counts, and height distributions
2. **Chronological Analysis**: Explore movie releases by year and actor birth statistics
3. **Genre Classification**: Use an AI model to predict movie genres based on title, cast, and other information

To use the genre classification feature:
- Click "Shuffle Movie" to select a random movie
- The app will automatically display the movie information and predict its genres
- The predictions will be compared with the actual genres from the database

## 7. Stopping the Ollama Server

When you're done using the app, you can stop the Ollama server:

```bash
# On macOS/Linux
pkill ollama

# Alternative for any OS
ps aux | grep ollama  # Find the process ID
kill -9 [process_ID]  # Replace with the actual ID
```