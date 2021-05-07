# EleNa (CS 520)
Elena Project for CS 520

## Installation And Usage

1. Install required dependencies
```Python
pip3 install -r requirements.txt
```

2. Run flask server
```Python
python3 app.py
```

3. Access server from `http://localhost:5000`

----

To run for production, use the following command instead:
```Python
python3 app.py --prod
```

## Documentation

To compile the documentation using Sphinx, run the following command from the top-level directory:
```
make docs
```
This will create a symbolic link in the top-level directory called `index.html` linking to the homepage of the documentation. Open it in your browser to view the docs.

You may need to clean up the existing compiled docs (especially if the source code has been modified) using the following:
```
make clean-docs
```
