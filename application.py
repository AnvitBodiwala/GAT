import matplotlib
from flask import Flask, render_template, request, redirect, url_for, jsonify

matplotlib.use('Agg')
import os
import nltkDraw
import SNA as sna
import xlrd
import tempfile
import csv
import json
import networkx as nx
from GAT_NLP import radar_runner
import GAT_GSA
import GAT_GSA.MapGenerator
#import GAT_GSA.GSA_flask
from numpy import array, matrix
import copy
import sys
import random
import GAT_NLP_JamesWu.parser as nlp_james
import scraper.url_parser as url_parser
from tzasacky_NLP import nlp_runner
# import Alok's and James' and Nikita's tools

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
#necessary line for flask apps
application = Flask(__name__)



# caseDict is the dictionary where we store the data for each case
# this is its structure:  {1:{case 1 data}, 2:{case 2 data}, etc.}
caseDict = {}

# tempdir is the main folder where we store temporary data, like user-uploaded files
# this is the structure of the temp folder:
# static/temp/
# 			tmp1038412/
#			tmp123t24/
# 			and all other temporary folders
#
# a temporary folder is created for each new case
tempdir = 'static/temp/'

# don't worry about this color shit. It's used by the SNA visualization
colors = ["DeepSkyBlue","Gold","ForestGreen","Ivory","DarkOrchid","Coral","DarkTurquoise","DarkCyan","Blue"]
hexColors = {}
for color in colors:
    rgbVal = matplotlib.colors.colorConverter.to_rgb(color)
    hexVal = matplotlib.colors.rgb2hex(rgbVal).replace("#","0x")
    hexColors[color] = hexVal

# the following few store helper methods are used to store user-uploaded files
# tempfile is a python package
# essentially what we're doing is copying their uploaded data to a randomly named folder or filename which is how we store it on the server
# then we use these folders and files to do our analysis
# some of the storing has to be done in a specialized manner, which is the reason for the storeNLP and storeGSA methods
def storefile(inFile):
    if inFile.filename == '':
        return
    suffix = '.' + inFile.filename.split('.')[-1]
    f = tempfile.NamedTemporaryFile(
            dir=tempdir,
            suffix=suffix,
            delete=False)
    inFile.save(f)
    return f.name

def storeNLP(file_list):
    if file_list[0].filename == '':
        return
    source_dir = tempfile.mkdtemp(dir=tempdir) + '/'
    for f in file_list:
        f.save(source_dir + f.filename)
    # this line is necessary because of how AWS creates default permissions for newly created files and folders
    os.chmod(source_dir, 0o755)
    return source_dir

def storeGSA(file_list):
    #saves everything but only returns the shapefile. Nice
    if file_list[0].filename == '':
        return
    source_dir = tempfile.mkdtemp(dir=tempdir) + '/'
    shapefile = None
    for f in file_list:
        f.save(source_dir + f.filename)
        if f.filename.endswith(".shp"):
            shapefile = source_dir + f.filename
    #see previous comment
    os.chmod(source_dir, 0o755)
    return shapefile

@application.route('/', methods = ['GET', 'POST'])
def upload():

    # each new "session" has a random case number associated with it
    # obviously, there is a small chance that case numbers will collide.
    # In that case, the person who used it second would overwrite the other persons data.
    # So this is not how it should be in its final version. But it's fine for now.
    case_num = 100000 + random.randint(0,100000)
    caseDict[case_num] = {}

    # this fileDict is where the case data, e.g. uploaded files, are stored
    fileDict = caseDict[case_num]

    # i.e. if a form has been submitted
    if request.method == 'POST':

        for f in request.files:
            print(str(f) + ": " + str(request.files.get(f)))

        # here the use of fileDict is probably more clear
        # the strings used to index request.files come from the HTML name of the input field
        # see upload.html
        fileDict['GSA_Input_CSV'] 		= storefile(request.files['GSA_Input_CSV'])
        fileDict['GSA_Input_SHP'] 		= storeGSA(request.files.getlist('GSA_Input_map'))
        fileDict['GSA_file_list']		= request.files.getlist('GSA_Input_map')
        fileDict['NLP_Input_corpus'] 	= storeNLP(request.files.getlist('NLP_Input_corpus'))
        fileDict['NLP_Input_LDP']		= storefile(request.files['NLP_Input_LDP'])
        fileDict['NLP_Input_Sentiment']	= storefile(request.files['NLP_Input_Sentiment'])

        #terms = request.form.get('NLP_LDP_terms')
        #term_array						= terms.split(',') if (terms != '' and terms != None) else None
        #if term_array != None:
        #    fileDict['NLP_LDP_terms']	= [term.strip() for term in term_array]

        fileDict["NLP_INPUT_NER"] = request.form.get("NLP_INPUT_NER")
        fileDict["NLP_INPUT_IOB"] = request.form.get("NLP_INPUT_IOB")

        fileDict['SNA_Input'] 			= storefile(request.files['SNA_Input'])
        #fileDict['NLP_Type'] 			= request.form['NLP_Type']

        fileDict['research_question'] 	= request.form.get('research_question')


        # for f in fileDict:
        # 	print(str(f) + ": " + str(request.files.get(f)))

        errors = checkExtensions(case_num) # helper method to make sure there are no input errors by the user
        # i.e. if there are errors, we can't proceed so we stay on the upload page
        if len(errors) > 0:
            return render_template('upload.html',
                errors = errors, case_num=case_num)

        # there are intermediary steps for SNA and NLP analyses
        if fileDict['SNA_Input']:
            return redirect(url_for('sheetSelect', case_num=case_num))

        # if a user does both SNA and NLP, as it stands, the NLP intermediary data will never be gotten to. This is a problem.
        if fileDict['NLP_Input_corpus']:
            return redirect(url_for('visualize', case_num=case_num))

        # if NLP chosen, allow them to pick from the different tools available
        # do i redirect to another url to choose then save the results then redirect to visualize?
        # no, just add the radio buttons under the file upload before the hr (in the template)
        return redirect(url_for('visualize', case_num=case_num))
    #fileDict doesn't mean the same thing anymore
    #fileDict.clear()
    return render_template("upload.html", case_num = case_num)

# the <int:case_num> is part of the URL
# why do we have case_num? Before, when we didn't, everyone accessing the webiste simultaneously was affecting the same internal data
# e.g. if person 1 made an SNA visuazliaiton, then person 2 came in a second later and did their SNA visualization, then
# person 2's data would overwrite person 1's data and person 1 would see person 2's data
# now, each person using GAT has a (almost certainly) unique case number associated with their internal data so this doesn't happen
# you can see, once you go past the upload page, the URL is appended with a number
@application.route('/choose_tropes/<int:case_num>', methods = ['GET', 'POST'])
def choose_tropes(case_num):
    fileDict = caseDict[case_num]
    NLP_dir = fileDict.get('NLP_Input_corpus')
    tropes = radar_runner.tropes(NLP_dir)

    if request.method == 'POST':
        chosen_tropes = []
        for trope in tropes:
            if request.form.get(trope[0]) == "on":
                chosen_tropes.append(trope)
        fileDict['tropes'] = chosen_tropes
        return redirect(url_for('visualize', case_num = case_num))

    return render_template("tropeselect.html", tropes = tropes, case_num = case_num)

@application.route('/radarvis/<int:case_num>')
def radarvis(case_num):
    fileDict = caseDict[case_num]
    images = fileDict.get('NLP_images')
    source_dir = fileDict.get('NLP_Input_corpus')
    for i in range(len(images)):
        images[i] = "/" + images[i]
    return render_template("radar.html", images = images, source_dir = source_dir, case_num = case_num)

@application.route('/visualize/<int:case_num>', methods = ['GET', 'POST'])
def visualize(case_num):
    fileDict = caseDict[case_num]
    GSA_file_CSV 		= fileDict.get('GSA_Input_CSV')
    GSA_file_SHP 		= fileDict.get('GSA_Input_SHP')
    GSA_file_SVG 		= fileDict.get('GSA_Input_SVG')
    NLP_dir 			= fileDict.get('NLP_Input_corpus')
    NLP_file_LDP		= fileDict.get('NLP_Input_LDP')
    NLP_urls                    = fileDict.get('NLP_LDP_terms')
    NLP_file_sentiment 	= fileDict.get('NLP_Input_Sentiment')
    NLP_NER_sentence 	= fileDict.get('NLP_INPUT_NER')
    NLP_IOB_sentence 	= fileDict.get('NLP_INPUT_IOB')
    SNA_file 			= fileDict.get('SNA_Input')
    #NLP_type 			= fileDict.get('NLP_Type')
    research_question 	= fileDict.get('research_question')
    tropes 				= fileDict.get('tropes')
    #research_question = None # temporary: Smart Search is under development
    graph 				= fileDict.get('graph')
    GSA_sample			= fileDict.get('GSA_data')
    error = False

    auto = None
    sp_dyn = None
    if GSA_sample != None:
        auto = GSA_sample[0:2]
        sp_dyn = [mat for mat in GSA_sample[2:]]
        calc_ac(case_num)


    if graph != None and len(graph.G)>0:

        if nx.algorithms.bipartite.is_bipartite(graph.G):
            graph.clustering()
        graph.closeness_centrality()
        graph.betweenness_centrality()
        graph.degree_centrality()
        #graph.katz_centrality()
        graph.eigenvector_centrality()
        graph.load_centrality()

    #if GSA_file.filename == '' and NLP_file.filename == '' and SNA_file.filename == '':
        #return("No files uploaded")

    #nb = None
    # if NLP_type == "Naive Bayes":
    # 	nb = Naive_Bayes.runNB(NLP_file.filename)

    #pa = None
    # if NLP_type == "Pattern Analyzer":
    # 	pa = Pattern_Analyzer.runPA(NLP_file.filename)

    #vs = None
    # if NLP_type == "Vader Sentiment":
    # 	vs = Vader_Sentiment.runVS(NLP_file.filename)

    #GSA functions
    # GSA_obs, GSA_weights, GSA_gamma, GSA_moran, GSA_geary = None, None, None, None, None

    # if GSA_file_CSV.filename != '' and GSA_file_SVG.filename != '':
    # 	GSA_obs, GSA_weights = AC.generateWeights(GSA_file_SVG.filename, GSA_file_CSV.filename, "ALL", 2000)
    # 	GSA_gamma = AC.gamma(GSA_obs, GSA_weights)
    # 	GSA_moran = AC.moran(GSA_obs, GSA_weights)
    # 	GSA_geary = AC.geary(GSA_obs, GSA_weights)

    #visualizations
    #nltkPlot = nltkDraw.plot(NLP_file_LDP, NLP_LDP_terms)
    jgdata, SNAbpPlot, attr, systemMeasures = SNA2Dand3D(graph, request, case_num, _2D = True)
    fileDict['SNAbpPlot'] = '/' + SNAbpPlot if SNAbpPlot != None else None
    fileDict['NLP_images'] = radar_runner.generate(NLP_dir, tropes)
    gsaCSV, mymap = tempParseGSA(GSA_file_CSV, GSA_file_SHP)
    if GSA_file_SVG != None:
        gsaCSV, mymap = parseGSA(GSA_file_CSV, GSA_file_SVG)

    if gsaCSV == None and mymap == True:
        error = True
        mymap = None
    ####################### Tye Zasacky NLP ##########################
    nlp_summary, nlp_entities, nlp_network, nlp_sources, nlp_tropes = None, None, None, None, None
    if NLP_dir:
        texts = nlp_runner.getTexts(NLP_dir)
        parsedDocs = nlp_runner.preProcess(texts)
        docs = parsedDocs['english']
        lexicon = nlp_runner.readLexicon()
        nlp_summary = nlp_runner.docSummary(docs)
        nlp_entities = nlp_runner.entitySentiment(docs)
        nlp_network = nlp_runner.sentimentGraph(docs)
        nlp_tropes = nlp_runner.emotionalValences(docs, lexicon)
 
    if NLP_urls:
        articles = nlp_runner.getArticles(NLP_urls)
        texts = [article.text for article in articles]
        parsedDocs = nlp_runner.preProcess(texts)
        docs = parsedDocs['english']
        lexicon = nlp_runner.readLexicon()
        nlp_summary = nlp_runner.docSummary(docs)
        nlp_entities = nlp_runner.entitySentiment(docs)
        #nlp_network = nlp_runner.sentimentGraph(docs)
        nlp_sources = nlp_runner.sourceAnalysis(articles)
        nlp_tropes = nlp_runner.emotionalValences(docs, lexicon)

    #################James WU's NLP methods:###########################
    nlp_sentiment = None
    if NLP_file_sentiment != None:
        import os.path
        if not os.path.isfile("nb_sentiment_classifier.pkl"):
            nlp_james.trainSentimentClassifier()
        with open(NLP_file_sentiment) as file:
            nlp_sentiment = nlp_james.predictSentiment(file.read())
    ####### To perform sentiment analysis on scraped data from URL - Ryan Steed 7 Jun 2017 #####
    '''
    if research_question[3] != None:
        print("Analyzing research question")
        import os.path
        if not os.path.isfile("nb_sentiment_classifier.pkl"):
            nlp_james.trainSentimentClassifier()
        nlp_sentiment = nlp_james.predictSentiment(research_question[3])
    '''
    ######Temporarily turned off as per Tony's request:##################
    ner = None
    if NLP_NER_sentence != None and NLP_NER_sentence.strip() != "":
        tags = nlp_james.npChunking(NLP_NER_sentence)
        ner = nlp_james.treeTraverseString(tags)
    #if request.method == 'POST':

    iob = None
    if NLP_IOB_sentence != None:
        ne_tree = nlp_james.NEChunker(NLP_IOB_sentence)
        iob = nlp_james.IOB_Tagging(ne_tree)
    ######Temporarily turned off as per Tony's request##################
    #################James WU's NLP methods###########################

    ###########scrape inputted url and return text:##############
    if research_question != None and research_question.strip() != "":
        print("RESEARCH QUESTION: " + research_question)
        research_question = url_parser.write_articles([research_question.strip()])

    research_question = research_question if research_question != None else None

    # pass files into parsers/tools created by Alok and James
    # this part will be done at the coding session
    # how will the output look?
    # oh yeah we need 3 different options for the 3 different NLP tools - DONE
    # go to http://werkzeug.pocoo.org/docs/0.11/datastructures/ to see how to read files
    # probably best to save the flask file objects as python file objects then use python file i/o
    # which should be widely documented

    # render different templates
    # or the same template with different things - THIS

    copy_of_graph = copy.deepcopy(graph)
    fileDict['copy_of_graph'] = copy_of_graph

    nlp_data_show = nlp_sentiment != None or ner != None or iob != None

    return render_template('visualizations.html',
        research_question = research_question,
        SNAbpPlot = SNAbpPlot,
        graph = copy_of_graph,
        attr = attr,
        colors = colors,
        #nltkPlot = nltkPlot,
        gsaCSV = gsaCSV,
        mymap = mymap,
        jgdata = jgdata,
        tropes = tropes,
        GSA_sample = GSA_sample,
        auto = auto,
        sp_dyn = sp_dyn,
        error=error,
        case_num = case_num,
        nlp_sentiment = nlp_sentiment,
        nlp_ner = ner,
        nlp_iob = iob,
        nlp_data_show = nlp_data_show,
        nlp_summary = nlp_summary,
        nlp_entities = nlp_entities,
        #nlp_network = nlp_network,
        nlp_sources =  nlp_sources,
        nlp_tropes = nlp_tropes
        )

@application.route('/help/<int:case_num>', methods = ['GET', 'POST'])
def help(case_num):
    return render_template('help.html', case_num = case_num)

@application.route('/contact/<int:case_num>', methods = ['GET', 'POST'])
def contact(case_num):
    return render_template('contact_us.html', case_num = case_num)
###########################
#### SNA input methods ####
###########################

@application.route('/sheet/<int:case_num>', methods = ['GET', 'POST'])
def sheetSelect(case_num):
    fileDict = caseDict[case_num]
    inputFile = fileDict['SNA_Input']
    workbook = xlrd.open_workbook(inputFile, on_demand = True)
    fileDict['sheets'] = workbook.sheet_names()

    # if workbook only has one sheet, the user shouldn't have to specify it
    if len(fileDict['sheets']) == 1:
        fileDict['nodeSheet'] = fileDict['sheets'][0]
        fileDict['attrSheet'] = None
        return redirect(url_for('nodeSelect', case_num = case_num))

    if request.method == 'POST':
        fileDict['nodeSheet'] = request.form.get('nodeSheet')
        fileDict['attrSheet'] = request.form.get('attrSheet')
        return redirect(url_for('nodeSelect', case_num = case_num))

    return render_template("sheetselect.html",
        sheets = fileDict['sheets'], case_num = case_num)

@application.route('/nodeinfo/<int:case_num>', methods = ['GET', 'POST'])
def nodeSelect(case_num):

    fileDict = caseDict[case_num]
    graph = sna.SNA( fileDict['SNA_Input'], nodeSheet = fileDict['nodeSheet'], attrSheet = fileDict['attrSheet'] )
    fileDict['graph'] = graph

    if request.method == 'POST':

        nodeColNames = []
        # Commented code is for multiple source columns
        # sourceColNames = []
        i = 0
        for header in graph.header:
            fileDict[header + "IsNode"] = True if request.form.get(header + "IsNode")=="on" else False
            # fileDict[header + "IsSource"] = True if request.form.get(header + "IsSource") == "on" else False
            #fileDict[header + "Class"] = request.form[header + "Class"]
            fileDict[header + "Name"] = request.form[header + "Name"]
            if fileDict[header + "IsNode"] == True:
                nodeColNames.append(fileDict[header + "Name"])
            # if fileDict[header + "IsSource"] == True:
            #     sourceColNames.append(fileDict[header + "Name"])
            i+=1
        fileDict['nodeColNames'] = nodeColNames
        # fileDict['sourceColNames'] = sourceColNames
        graph.createNodeList(nodeColNames)
        graph.createEdgeList(nodeColNames[0])
        if fileDict['attrSheet'] != None:
            graph.loadAttributes()
            graph.calculatePropensities(emo=True)
        # Only the first column is a source
        graph.closeness_centrality()
        graph.degree_centrality()
        graph.betweenness_centrality()
        return redirect(url_for('visualize', case_num=case_num))

    return render_template("nodeselect.html",
        nodes = graph.header, case_num = case_num)

@application.route('/edgeinfo/<int:case_num>', methods = ['GET', 'POST'])
def edgeSelect(case_num):
    import warnings
    warnings.warn("deprecated", DeprecationWarning, stacklevel=2) # deprecated by Ryan Steed 20 Jul 2017, replaced by check box in nodeselect.html
    fileDict = caseDict[case_num]
    graph = fileDict['graph']
    combos = fileDict['nodeColNames']
    fileDict['combos'] = combos

    if request.method == 'POST':
        for combo in combos:
            if request.form.get(combo) == "on":
                graph.createEdgeList(combo)

        graph.closeness_centrality()
        graph.degree_centrality()
        graph.betweenness_centrality()

        return redirect(url_for('visualize', case_num = case_num))


    return render_template("edgeselect.html",
        combos = combos, case_num = case_num)

def allCombos(n, case_num): # deprecated
    fileDict = caseDict[case_num]
    graph = fileDict['graph']
    h = graph.header
    combos = []
    for i in range(len(n)):
        for j in range(i+1,len(n)):
            combos.append((n[i], n[j], fileDict[h[n[i]] + "Name"] + " x " + fileDict[h[n[j]] + "Name"]))

    return combos

def SNA2Dplot(graph, request, label=False):
    attr = {}
    if graph == None:
        return None
    if request.form.get("options") == None:
        i = 0
        for nodeSet in graph.nodeSet:
            attr[nodeSet] = [colors[i],50]
            i += 1
            if i > len(colors) + 1:
                i = 0
    else:
        for nodeSet in graph.nodeSet:
            c = request.form.get(nodeSet + "Color")
            attr[nodeSet] = [c,50]

    return graph.plot_2D(attr, label=label)

# makes more sense to make a whole SNA viz method that outputs both 2D and 3D if so desired
# 2D is probably not desired in any case though
def SNA2Dand3D(graph, request, case_num, _3D = True, _2D = False, label = False):
    fileDict = caseDict[case_num]
    systemMeasures = {}

    if graph == None:
        return None, None, None

    #make both
    attr = {}
    colorInput = []

    if request.form.get("options") == None:
        i = 0
        for nodeSet in graph.nodeSet:
            attr[nodeSet] = [colors[i],50]
            colorInput.append(hexColors[colors[i]])
            i += 1
            if i == 8:
                i = 0
    else:
        for nodeSet in graph.nodeSet:
                attr[nodeSet] = [request.form.get(nodeSet + "Color"),50]
                c = request.form.get(nodeSet + "Color")
                colorInput.append(hexColors[c])

    if request.form.get("removeNodeSubmit") != None:
        print("Removing node...")
        graph.removeNode(request.form.get("a"))

    # Get new node info, if available
    if request.form.get("addNodeSubmit") != None:
        print("Requesting new node data...")

        node = request.form.get("nodeName")

        attrDict = {
            'block': request.form.get("nodeSet")
        }
        i = 0
        while (request.form.get("attribute"+str(i)) is not None) and (request.form.get("attribute"+str(i)) != '') and (request.form.get("value"+str(i)) is not None) and (request.form.get("value"+str(i)) != ''):
            key = request.form.get("attribute"+str(i))
            value = request.form.get("value"+str(i))
            if request.form.get("weight"+str(i)) is not None and request.form.get("weight"+str(i)) != '':
                value = [value,{'W':request.form.get("weight"+str(i))}]
            dictForm = {key: value}
            attrDict.update(dictForm)
            i += 1

        links = []
        j = 0
        while request.form.get("link"+str(j)) != None:
            links.append(request.form.get("link"+str(j)))
            j += 1

        print("node, attrDict, connections",node,attrDict,links)
        graph.addNode(node,attrDict,links)

    # Add system measures dictionary
    # systemMeasures["Node Connectivity"] = graph.node_connectivity() # Currently only returning zero...
    systemMeasures["Average Clustering"] = graph.average_clustering()
    # systemMeasures["Attribute Assortivity"] = graph.attribute_assortivity() # Which attributes...? UI?
    if graph.is_strongly_connected():
        systemMeasures["Connection Strength"] = "Strong"
    elif graph.is_weakly_connected():
        systemMeasures["Connection Strength"] = "Weak"

    # Add system measures descriptions to dictionary
    systemMeasures["Description"] = {
        'Average Clustering': 'A high clustering coefficient indicates that actors within the network are closely connected to a statistically significant degree. It is a sophisticated measure of the density of a network.',
        'Connection Strength': 'Knowing whether a graph is strongly or weakly connected is helpful because it demonstrates the robustness of the graph based on its redundancy. If a graph is strongly connected, there are two links between each actor in the network, one in each direction. A strongly connected graph thus would likely have more redundant communication/information flow and be more difficult to perturb than a weakly connected graph.',
        'Resilience':'The baseline value for resilience is determined by identifying the cliques associated with the most central nodes in the network, perturbing those subgraphs, and measuring the mean shortest path average over several perturbations. The results are scaled on a normal curve across all cliques and a percentile resilience is determined for each clique. A high percentile resilience denotes resilience to perturbation. These values are visualized on a color spectrum from red to blue, where red is low relative resilience and blue is high relative resilience.',
        'AddNode': 'Introduces a new node to the network, complete with a user-defined name, user-defined attributes and known links. Using the DRAG link prediction model, node attributes are used to form likely connections and intelligently model the effects of external change on the network. New nodes and their predicted links are colored red for easy identification.',
        'RemoveNode':'Removes the node inputted in the box below and any links to which it belongs.',
        'eigenvector':'Centrality measure which sums the centralities of all adjacent nodes',
    }

    # Calculate resilience when requested
    if request.form.get("resilienceSubmit") != None:
        try:
            systemMeasures["Resilience"] = graph.averagePathRes(iters=5) # gets a scaled resilience value for each clique identified in network
            # Add colors for each resilience measure
            for cluster in systemMeasures["Resilience"]:
                systemMeasures["Resilience"][cluster] = int(systemMeasures["Resilience"][cluster])
                percentile = systemMeasures["Resilience"][cluster]
                b = int(percentile)
                r = int(100 - percentile)
                systemMeasures["Resilience"][cluster] = [percentile,r,b]
        except nx.exception.NetworkXError:
            systemMeasures["Resilience"] = "Could not calculate resilience, NetworkX error."


    copy_of_graph = copy.deepcopy(graph)
    fileDict['copy_of_graph'] = copy_of_graph
    #return based on inputs
    ret3D = graph.create_json(graph.nodeSet, colorInput) if _3D else None
    label = True if not label and len(graph.nodes) < 20 else False
    ret2D = graph.plot_2D(attr, label) if _2D else None
    fileDict['jgdata'] = ret3D

    return ret3D, ret2D, attr, systemMeasures


@application.route('/snaviz/<int:case_num>', methods = ['GET', 'POST'])
def jgvis(case_num):
    fileDict = caseDict[case_num]
    #jgdata = fileDict.get('jgdata')
    graph = fileDict.get('copy_of_graph')
    jgdata, SNAbpPlot, attr, systemMeasures = SNA2Dand3D(graph, request, case_num, _2D = False)
    if request.method == 'POST':
        jgdata, SNAbpPlot, attr, systemMeasures = SNA2Dand3D(graph, request, case_num, _2D = True)
    return render_template("Jgraph.html",
            jgdata = jgdata,
            SNAbpPlot = SNAbpPlot,
            attr = attr,
            graph = graph,
            colors = colors,
            case_num = case_num,
            systemMeasures = systemMeasures
        )

@application.route("/_get_node_data/<int:case_num>")
def get_node_data(case_num):
    fileDict = caseDict[case_num]
    graph = fileDict.get('copy_of_graph')
    name = request.args.get('name', '', type=str)
    if graph == None or len(graph.G) == 0:
        return jsonify(	name=name,
                        eigenvector=eigenvector,
                        betweenness=betweenness
                        )
    graph.closeness_centrality()
    graph.betweenness_centrality()
    graph.degree_centrality()
    # graph.katz_centrality()
    graph.eigenvector_centrality()
    graph.load_centrality()
    if graph.eigenvector_centrality_dict != {} and graph.eigenvector_centrality_dict != None:
        eigenvector = str(round(graph.eigenvector_centrality_dict.get(name),4));
    else:
        eigenvector="clustering not available"
    if graph.betweenness_centrality_dict != {} and graph.betweenness_centrality_dict != None:
        betweenness = str(round(graph.betweenness_centrality_dict.get(name),4));
    else:
        betweenness="clustering not available"
    attributes = graph.get_node_attributes(name)
    toJsonify = dict(name=name,
                     eigenvector=eigenvector,
                     betweenness=betweenness,
                     attributes=attributes)
    return jsonify(toJsonify)

@application.route("/_get_edge_data/<int:case_num>")
def get_edge_data(case_num):
    fileDict = caseDict[case_num]
    graph = fileDict.get('copy_of_graph')
    name = request.args.get('name', '', type=str)
    if graph == None or len(graph.G) == 0:
        return jsonify(name=name)
    pair = name.split(",")
    link = graph.G[pair[0]][pair[1]]
    toJsonify = dict(name=name,source=pair[0],target=pair[1])
    for attr in link:
        toJsonify[attr] = link[attr]
    return jsonify(toJsonify)

@application.route("/_get_autocorrelation/<int:case_num>")
def get_autocorrelation(case_num):
    fileDict = caseDict[case_num]
    GSA_file_CSV = fileDict.get('GSA_Input_CSV')
    GSA_file_SHP = fileDict.get('GSA_Input_SHP')
    year = request.args.get('year',0,type=int)
    if year != 0:
        loc, glob = fileDict['ac'][year]
        return jsonify(year = year, loc = loc, glob = glob)
    return jsonify(year="something went wrong", loc = 0, glob = 0)

def calc_ac(case_num):
    fileDict = caseDict[case_num]
    GSA_file_CSV = fileDict.get('GSA_Input_CSV')
    GSA_file_SHP = fileDict.get('GSA_Input_SHP')
    y1 = 1929
    yn = 2010
    fileDict['ac'] = {}
    for year in range(y1,yn):
        fileDict['ac'][year] = tuple(GSA_sample_autocorrelation[year-y1])
    return


#####################
#### GSA methods ####
#####################

def tempParseGSA(GSA_file_CSV, GSA_file_SHP):
    if GSA_file_CSV == None or GSA_file_SHP == None:
        return (None, None)

    gsaCSV = []
    with open(GSA_file_CSV) as csvfile:
        try:
            reader = csv.reader(csvfile)
            for row in reader:
                gsaCSV.append(row)
        except:
            return (None, True)

    gsaSVG = os.path.dirname(GSA_file_SHP) + "/mymap.svg"
    GAT_GSA.MapGenerator.generateMap(GSA_file_SHP, gsaSVG)


    with open(gsaSVG, 'r') as myfile:
        data = None
        try:
            data = myfile.read()
        except:
            return (None, True)
    #print(data.replace('"', "'"))
    data = data.replace('"', "'")
    return json.dumps(gsaCSV), json.dumps(data)


def parseGSA(GSA_file_CSV, GSA_file_SVG):

    if GSA_file_CSV == None or GSA_file_SVG == None:
        print("csv or svg is none")
        return (None, None)

    gsaCSV = []
    with open(GSA_file_CSV) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            gsaCSV.append(row)

    with open(GSA_file_SVG, 'r') as myfile:
        data = myfile.read()
    #print(data.replace('"', "'"))
    data = data.replace('"', "'")
    return json.dumps(gsaCSV), json.dumps(data)

########################
#### Sample methods ####
########################

@application.route('/sample/<int:case_num>/<path:sample_path>')
def sample(sample_path, case_num):
    fileDict = caseDict[case_num]
    arr = sample_path.split('/')
    if arr[0] == 'GSA':
        fileDict['GSA_Input_CSV'] = url_for('static', filename = "sample/GSA/" + arr[1])[1:]
        fileDict['GSA_Input_SHP'] = url_for('static', filename = "sample/GSA/" + arr[2])[1:]
        fileDict['GSA_data'] = (0.001, 0.002, array([[ 252.,   27.,    1.,    0.,    0.],
       [  28.,  226.,   20.,    0.,    0.],
       [   1.,   25.,  239.,   15.,    0.],
       [   0.,    0.,   18.,  237.,   22.],
       [   0.,    0.,    0.,   24.,  257.]]), matrix([[ 0.9       ,  0.09642857,  0.00357143,  0.        ,  0.        ],
        [ 0.10218978,  0.82481752,  0.0729927 ,  0.        ,  0.        ],
        [ 0.00357143,  0.08928571,  0.85357143,  0.05357143,  0.        ],
        [ 0.        ,  0.        ,  0.06498195,  0.85559567,  0.07942238],
        [ 0.        ,  0.        ,  0.        ,  0.08540925,  0.91459075]]), array([[ 0.31780822,  0.26712329,  0.13561644,  0.23013699,  0.04931507],
       [ 0.32951514,  0.25812019,  0.13180606,  0.1625608 ,  0.1179978 ],
       [ 0.3007761 ,  0.26782838,  0.22843755,  0.16869234,  0.03426563],
       [ 0.29380902,  0.25603358,  0.30535152,  0.03903463,  0.10577125],
       [-0.        ,  0.09811321,  0.09433962,  0.25660377,  0.5509434 ]]), matrix([[   3.98789072,   11.01167278,   35.43877551,  100.43628118,
          166.20696764],
        [  28.92208853,    4.19293283,   26.38095238,   91.37845805,
          157.14914451],
        [  55.71301248,   28.32683784,    5.07303106,   64.99750567,
          130.76819213],
        [  85.41208655,   58.02591192,   29.69907407,    6.15356836,
           65.77068646],
        [  97.12041989,   69.73424525,   41.40740741,   11.70833333,
            6.61742518]]))
        #return fileDict['GSA_file_CSV'] + " " + fileDict['GSA_file_SVG']
    if arr[0] == 'NLP':
        if arr[1] == 'iran':
            fileDict['NLP_Input_Sentiment'] = 'static/sample/NLP/sample_sentiment.txt'
            return redirect(url_for('visualize', case_num = case_num))
        else:
            fileDict['NLP_Input_corpus'] = url_for('static', filename = "sample/NLP/" + arr[1] + '/')[1:]
            return redirect(url_for('visualize', case_num = case_num))
    if arr[0] == 'SNA':
        fileDict['SNA_Input'] = url_for('static', filename = "sample/SNA/" + arr[1])[1:]
        return redirect(url_for('sheetSelect', case_num = case_num))


    return redirect(url_for('visualize', case_num = case_num))

########################
#### Helper methods ####
########################

def checkExtensions(case_num):

    errors = []
    fileDict = caseDict[case_num]
    gsa_csv_file = fileDict['GSA_Input_CSV']
    if gsa_csv_file != None:
        if not gsa_csv_file.endswith('.csv'):
            errors.append("Error: please upload csv file for GSA.")

    gsa_file_list = fileDict['GSA_file_list']
    exts = ['.shp', '.shx', '.dbf']
    if gsa_file_list[0].filename != '':
        for ext in exts:
            ext_in = False
            for f in gsa_file_list:
                if f.filename.endswith(ext):
                    ext_in = True
            if not ext_in:
                errors.append("Error: please upload shp, shx, and dbf file for GSA.")
                break

    sna_file = fileDict['SNA_Input']
    if sna_file != None:
        if not sna_file.endswith(('.xls','.xlsx')):
            errors.append("Error: please upload xls OR xlsx file for SNA.")

    nlp_file = fileDict['NLP_Input_LDP']
    #terms = fileDict.get('NLP_LDP_terms')
    #if nlp_file != None:
    #    if not nlp_file.endswith('.txt'):
    #        errors.append("Error: please upload txt file for NLP Lexical Dispersion Plot.")

    sentiment_file = fileDict["NLP_Input_Sentiment"]
    if sentiment_file != None:
        if not sentiment_file.endswith('.txt'):
            errors.append("Error: please upload txt file for Sentiment Analysis.")

    if terms != None and nlp_file == None:
        errors.append("Error: please upload txt file for NLP Lexical Dispersion Plot.")

    return errors

GSA_sample_autocorrelation=[
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.002],
[0.001, 0.002],
[0.002, 0.003],
[0.01 ,0.005],
[0.003, 0.006],
[0.005, 0.005],
[0.004, 0.002],
[0.002, 0.003],
[0.001, 0.002],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.003, 0.001],
[0.001, 0.001],
[0.001, 0.001],
[0.002, 0.002],
[0.001, 0.003],
[0.001, 0.002],
[0.001, 0.001],
[0.002, 0.001],
[0.001, 0.001],
[0.001, 0.002],
[0.001, 0.001],
[0.001, 0.002],
[0.001, 0.001],
[0.001, 0.001],
[0.001, 0.001]]

@application.route('/regionalization/<int:case_num>')
def reg(case_num):
    return render_template("regionalization-test.html", case_num = case_num)

#################
#### Running ####
#################


application.secret_key = 'na3928ewafds'


if __name__ == "__main__":
    application.debug = True
    application.run(threaded=True)
