Small agent to pick a horror movie from the 80s

You need to fill in the root directory a valid .env file. Copy the existing `.env.template` and 
fill it with your values.

It uses TMDB (https://www.themoviedb.org) to select movies, and then filters them using a 
decision model to see if they are adequate. 

Create a token for TMDB to be able to query it.

As the LLM for the Agent uses Ollama (https://ollama.com/) running a local model (qwen3.5:4b). Once installed
Ollama, pull the model by running

    ollama pull qwen3.5:4b

You can decide what to use for the decision model, setting the adequate keys in .env

You can use 
* `jev` 
   please fill your TYPESAFE_API_KEY from https://typesafe.ai ) in `.env` file
* `ollama` 
   download the default model with 

     ollama pull tev1

* `openai`
   fille your OPENAI_API_KEY (https://openai.com) in `.env` file


Install the dependencies and run the script with

    uv venv
    uv pip install -r requirements.txt
    uv run two/movie_picker.py


Enjoy!
