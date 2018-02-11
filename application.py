import matplotlib

matplotlib.use('Agg')

from flask import Flask

from gat.view.gsa import gsa_blueprint
from gat.view.info import info_blueprint
from gat.view.log import log_blueprint
from gat.view.sample import sample_blueprint
from gat.view.sna import sna_blueprint
from gat.view.upload import upload_blueprint
from gat.view.visualize import visualize_blueprint
from gat.view.out import out_blueprint
from gat.view.smart_search import smart_search_blueprint
from gat.view.nlp import nlp_blueprint

''' Before running:
        Make sure you have flask and jinja2 installed
        among other things
        They should be in the Anaconda distribution
    How to run:
        > python application.py
        Then, open a browser and go to http://127.0.0.1:5000
        You should see the web app
    Current status
        Can't resize stuff to be smaller than its original set size (limitation of html)
        If you search for a node, color is reset to default blue green red etc. Needs to change (later though)
'''

''' Ideas:
        Use divs to represent different containers (NLP, SNA, GSA, etc.). Follow online tutorials for draggable things
        Embed JS in the html code to make this easier.

        matplotlib: http://cfss.uchicago.edu/slides/week10_flaskPlotting.pdf

        Couple options: Do we run all things that we can run, then when the user asks for them we just show?
        Or do we perform the function when they choose it?
        The first seems easier for me, but less efficient and intuitive overall.
        For the second, I'd have to find a way to run the programs by pressing a menu button
        CS250 design decisions popping up here no?

        Users will log in?
        We can save their files in their user directory

        Big things:
            Saving files on server so we can upload files that aren't in the same directory as the other
            Managing said files. Some we don't want to save, right? They'll take up a ton of space
            SNA prompts
            Alok's request about Twitter things
            putting the app on the duke server

        http://flask.pocoo.org/docs/0.11/quickstart/#file-uploads

        What to comment:
            fileDict and caseDict
            case_num
            colors
            storefile helper methods
            general flask stuff
            Dylan probably doesn't need to know too much about the specfic components

        Flask stuff:
            render_template() displays the specified HTML template with whatever data you pass to it
            arguments passed into render_template() can be then displayed/used in the HTML template
            the HTML template engine, Jinja, interprets None as False in a boolean statement
            So if you have {% if var %} and var does not exist, then it will interpret var as false.

            redirect goes to the specified URL, and runs its associated python method

'''
application = Flask(__name__)
application.register_blueprint(log_blueprint, url_prefix='/log')
application.register_blueprint(info_blueprint)
application.register_blueprint(upload_blueprint)
application.register_blueprint(visualize_blueprint)
application.register_blueprint(sample_blueprint, url_prefix='/sample')
application.register_blueprint(sna_blueprint)
application.register_blueprint(gsa_blueprint)
application.register_blueprint(out_blueprint)
application.register_blueprint(smart_search_blueprint)
application.register_blueprint(nlp_blueprint)

#################
#### Running ####
#################

application.secret_key = 'na3928ewafds'

if __name__ == "__main__":
    application.debug = True
    application.run(host='127.0.0.1', threaded=False, port=5000)
