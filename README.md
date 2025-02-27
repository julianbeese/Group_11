# Advanced Programming for Data Science - Project 1

This project is built using Python and requires specific dependencies. Follow these steps to set up your development environment:

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

## 3. Run Tests

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

## 4. Run the Streamlit App

To start the Streamlit application, ensure your virtual environment is activated and run:

```bash
streamlit run app.py
```

This will launch the Streamlit app in your default web browser. **And automatically check if the necessary data is in the /data folder. If not, it will download the data from the internet. (src/__init__.py)**