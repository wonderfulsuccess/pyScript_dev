#How to run
1. run as debuge mode:
sudo FLASK_APP=flaskElastick.py FLASK_DEBUG=1 python3 -m flask run
2. run as an app:
 export FLASK_APP=appName.py 
flask run --host=0.0.0.0
flask run

#Control
flaskElastic.py:
1. APP entrance
2. router control purpuse
3. html template rendering

#Model
mode.py
1. communicate with ES for data fetching and update

#View
/template
There is mo javascript code now, just htmls and one css called w3.css. Anyway it satisfied me. JS will be included for speed up consideration


#NLP
nlp is implemented in ./analysis for word2vector and similarity based on gensim. A lot of models were saved in ./analysis/trained_model/ many things can be done to improve the response speed here :)


