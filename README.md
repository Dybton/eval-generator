### How to run this project

1. Install and run conda
2. Create conda env and activate it
3. Set your open open AI env variable
4. Install all requirements via pip requirements.txt
5. Start the project via FastAPI: dev main.py
6. Run code via the endpoints in main, e.g.: http://127.0.0.1:8000/hybrid-chunker

### How to create eval sets

1. Add the file to process to files/1_raw_files
2. Go to main.py and find the generate-eval-dataset endpoint
3. Change the file name and the document language
4. Add http://127.0.0.1:8000/generate-eval-dataset to the URL and wait. When it's done, it should generate a JSON in 4_enriched_files
5. Take this file and go to the proposal-rag next project and add it to the enriched files folder
6. Go to gen-eval.tsx and change the filename variable to match the name
7. Go to http://localhost:3000/gen-eval
8. From here, you can press up and down once you have deselected the text fields. This will toggle the chunks and the associated requirements, etc.
9. The idea is that you can edit the fields and that will directly edit the file in the enriched files folder
