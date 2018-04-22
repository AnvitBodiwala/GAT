import copy
import gc
from flask import Blueprint, render_template, request

from gat.dao import dao
from gat.service import scraper_service, sna_service, gsa_service, nlp_service, NLP_TO_NETWORK, NLP_OTHER_PREP

visualize_blueprint = Blueprint('visualize_blueprint', __name__)


@visualize_blueprint.route('/visualize', methods=['GET', 'POST'])
def visualize():
    case_num = request.args.get('case_num', None)
    if not case_num:
        case_num = request.form.get('case_num', None)
    fileDict = dao.getFileDict(case_num)

    GSA_file_CSV = fileDict.get('GSA_Input_CSV')
    GSA_file_SHP = fileDict.get('GSA_Input_SHP')
    GSA_file_SVG = fileDict.get('GSA_Input_SVG')
    NLP_dir = fileDict.get('NLP_Input_corpus')
    NLP_urls = fileDict.get('NLP_LDP_terms')
    NLP_file_sentiment = fileDict.get('NLP_Input_Sentiment')
    NLP_new_example_file = fileDict.get('NLP_New_Example')
    research_question = fileDict.get('research_question')
    tropes = fileDict.get('tropes')
    graph = fileDict.get('graph')
    GSA_sample = fileDict.get('GSA_data')
    network_sample = fileDict.get('Geonet_Input_Streets')
    error = False

    auto = None
    sp_dyn = None
    svgNaming = None
    if GSA_sample != None:
        svgNaming = GSA_sample[0]
        auto = GSA_sample[1:3]
        sp_dyn = [mat for mat in GSA_sample[3:]]

    gsaCSV = None
    mymap = None
    nameMapping = None

    if (GSA_file_CSV is not None and GSA_file_SHP is not None and fileDict.get('GSA_meta') is not None):
        gsaCSV, mymap, nameMapping = gsa_service.tempParseGSA(GSA_file_CSV, GSA_file_SHP, fileDict['GSA_meta'][0],
                                                              fileDict['GSA_meta'][1])

    if GSA_file_SVG is not None:
        gsaCSV, mymap = gsa_service.parseGSA(GSA_file_CSV, GSA_file_SVG)

    if gsaCSV is None and mymap == True:
        error = True
        mymap = None

    sna_service.prep(graph)
    jgdata, SNAbpPlot, attr, systemMeasures = sna_service.SNA2Dand3D(graph, request, case_num, _2D=True)
    fileDict['SNAbpPlot'] = '/' + SNAbpPlot if SNAbpPlot is not None else None

    copy_of_graph = copy.deepcopy(graph)
    fileDict['copy_of_graph'] = copy_of_graph

    if NLP_dir:
        nlp_summary, nlp_entities, nlp_network, nlp_sources, nlp_tropes= nlp_service.nlp_dir(NLP_dir)
    else:
        nlp_summary, nlp_entities, nlp_network, nlp_sources, nlp_tropes= nlp_service.nlp_urls(NLP_urls)

    nlp_sentiment = nlp_service.sentiment(NLP_file_sentiment)
    research_question = scraper_service.scrape(research_question)

    geoNet = None
    if network_sample is not None:
        geoNet = gsa_service.geoNetwork(case_num=case_num)

    actors = None
    relations = None
    if "emotionalSpace" in fileDict:
        actors, relations = gsa_service.emoSpace(case_num=case_num)

    nlp_new_example_sentiment = ''
    nlp_new_example_relationship = ''

    nlp_stemmerize = None
    nlp_lemmatize = None
    nlp_abstract = None
    nlp_top20_verbs = None
    nlp_top20_persons = None
    nlp_top20_locations = None
    nlp_top20_organizations = None
    nlp_sentence_sentiment_distribution = None
    nlp_wordcloud = None

    if NLP_new_example_file is not None:
        nlp_new_example_sentiment = NLP_TO_NETWORK.sentiment_mining(NLP_new_example_file)
        
        gc.collect()
        nlp_new_example_relationship = NLP_TO_NETWORK.relationship_mining(NLP_new_example_file)

        gc.collect()
        nlp_stemmerize, nlp_lemmatize, nlp_abstract, nlp_top20_verbs, nlp_top20_persons, nlp_top20_locations, nlp_top20_organizations, nlp_sentence_sentiment_distribution, nlp_wordcloud = NLP_OTHER_PREP.getNLPOTHER(NLP_new_example_file)
        
        gc.collect()
        nlp_summary = 'Enable'

    #call gsa_service.geoNet, produce output, do whatever else you need
    #geoNet = true if there is a geonet produced
    # fileDict[geoNetFiles...]
    return render_template('visualizations.html',
                           nlp_stemmerize=nlp_stemmerize,
                           nlp_lemmatize=nlp_lemmatize,
                           nlp_abstract=nlp_abstract,
                           nlp_top20_verbs=nlp_top20_verbs,
                           nlp_top20_persons=nlp_top20_persons,
                           nlp_top20_locations=nlp_top20_locations,
                           nlp_top20_organizations=nlp_top20_organizations,
                           nlp_sentence_sentiment_distribution=nlp_sentence_sentiment_distribution,
                           nlp_wordcloud=nlp_wordcloud,
                           research_question=research_question,
                           SNAbpPlot=SNAbpPlot,
                           graph=copy_of_graph,
                           attr=attr,
                           colors=sna_service.colors,
                           gsaCSV=gsaCSV,
                           mymap=mymap,
                           svgNaming=svgNaming,
                           nameMapping=nameMapping,
                           jgdata=jgdata,
                           tropes=tropes,
                           GSA_sample=GSA_sample,
                           auto=auto,
                           sp_dyn=sp_dyn,
                           error=error,
                           case_num=case_num,
                           nlp_sentiment=nlp_sentiment,
                           nlp_summary=nlp_summary,
                           nlp_entities=nlp_entities,
                           nlp_sources=nlp_sources,
                           nlp_tropes=nlp_tropes,
                           systemMeasures=systemMeasures,
                           NLP_new_example_file=NLP_new_example_file,
                           nlp_new_example_sentiment=nlp_new_example_sentiment,
                           nlp_new_example_relationship=nlp_new_example_relationship,
                           geoNet=geoNet,
                           actors=actors,
                           relations=relations)
