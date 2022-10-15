# fetch-take-home
 
There are 3 files for this project. To run the project you will need:
1. <a href="https://www.python.org/downloads/">python</a> and a prompt like <a href="https://docs.anaconda.com/anaconda/install/index.html">Anaconda</a>
2. Flask <code> pip install Flask </code>
3. Jupyter notebook <code> pip install notebook </code>

<code> unittests.py </code> contains the unit tests for the main logic used in the APIs
<code> server.py </code> contains the API endpoints and their logic
<code> fetch-take-home.ipynb </code> contains the example client with actual output. This also is where someone can test the server APIs if they wish

I suggest running the files in this order

<code> unittests.py </code>
1. In a command prompt, navigate to the folder that contains the 3 files.
2. Type <code> python unittests.py </code> in the prompt and hit enter
3. Verify that all 8 tests pass

<code> server.py </code>
1. In the same command prompt, type <code> python server.py </code>
2. A server on your machine will be spun up and the prompt will tell you what IP the server is running on

 <code> fetch-take-home.ipynb </code>
 1. Open the notebook (In a new command prompt [since the other is running the server] navigate to where the files are and type <code> jupyer notebook</code> into the prompt. From there a page in your browser will open and you can click on the notebook)
 2. Observe the output from my machine in cells 1 & 2
 4. Comment out cells 1 & 2
 5. Put your IP (from the <code>server.py</code> step 2 above) into cell 3
 6. Uncomment the code in cell 4
 7. Run cell 4
