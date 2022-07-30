import getopt, sys, os, json, signal
import logging
import click
from flask import Flask
from flask import request, Response
from flask import render_template, jsonify
from flask_cors import CORS, cross_origin

os.system("")
CEND    = '\33[0m'
CGREY   = '\33[90m'
CRED    = '\33[91m'
CGREEN  = '\33[92m'
CYELLOW = '\33[93m'
CBLUE   = '\33[94m'
CVIOLET = '\33[35m'
CBEIGE  = '\33[36m'
CWHITE  = '\33[37m'

# change directory to the location of the script
os.chdir(os.path.dirname(__file__))


def secho(text, file=None, nl=None, err=None, color=None, **styles):
    pass

def echo(text, file=None, nl=None, err=None, color=None, **styles):
    pass

click.echo = echo
click.secho = secho

# Remove 1st argument from the
# list of command line arguments
argumentList = sys.argv[1:]
 
# Options
options = "hsgn:p:m:"
 
# Long options
long_options = ["help", "silent", "gpu", "host =", "port =", "model ="]
status = "ready"
silent=False
port=14377
host='0.0.0.0'
gpu=False
selectedModel = "default"

def translate(translator, text):
    result = translator.translate(text)
    return result

def file_len(fname):
    if not os.path.isfile(fname):
        return 0
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

# source is accessible file from server
def batchTranslate(translator, source):
    if not os.path.isfile(source):
        print("Error! File", source, "is not exist!")
        return

    temp = source + ".res~"
    result = source + ".res"

    def complete():
        print("Batch complete! Result is:", result)
        return result

    if os.path.isfile(result):
        return complete()

    currentProgress = 0
    existingProgress = file_len(temp)
    tempFile  = open(temp, 'a', encoding="UTF-8")

    print("Existing progress is", existingProgress)
    with open(source, encoding="UTF-8") as infile:
        for line in infile:
            if (currentProgress < existingProgress):
                currentProgress += 1
                continue

            #print(line)
            thisObj = json.loads(line)
            print("Job",currentProgress, "translating:", thisObj["text"])
            thisObj["text"] = translate(translator, thisObj["text"])
            tempFile.write(json.dumps(thisObj)+"\n")
            currentProgress += 1
    tempFile.close()
    os.rename(temp, result)
    return complete()


def runService(host, port, gpu, silent):
    from fairseq.models.transformer import TransformerModel
    log = logging.getLogger('fairseq.models.fairseq_model')
    log.setLevel(logging.ERROR)

    ja2en = TransformerModel.from_pretrained(
        '../models/sugoi-fairseq-3.3/japaneseModel/',
        checkpoint_file='big.pretrain.pt',
        source_lang = "ja",
        target_lang = "en",
        bpe='sentencepiece',
        sentencepiece_model='../models/sugoi-fairseq-3.3/sp_model/spm.ja.nopretok.model',
        no_repeat_ngram_size=3,
        beam=5
        # replace_unk=True
        # is_gpu=True
    )
    if gpu:
        ja2en.cuda()

    app = Flask(__name__)
    cors = CORS(app)    
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)


    def run_on_start(*args, **argv):
        app.logger.info("Server has started!")
    run_on_start()

    @app.before_first_request
    def before_first_request():
        app.logger.info("before_first_request")
    
    @app.route("/", methods = ['GET'])
    def index():
        f = open("./templates/index.html", "r")
        return f.read()
        #return render_template("index.html")

    @app.route("/favicon.ico", methods = ['GET'])
    def getFavicon():
        f = open("./templates/favicon.ico", "rb")
        return Response(f.read(), mimetype='image/x-icon')  
        #return render_template("index.html")

    @app.route("/status", methods = ['GET'])
    def status():
        return Response("READY", mimetype='text/plain')

    @app.route("/shutdown", methods = ['GET'])
    def shutdown():
        os.kill(os.getpid(), signal.SIGINT)
        return Response("READY", mimetype='text/plain')    


    app.config['CORS_HEADERS'] = 'Content-Type'

    @app.route("/translate", methods = ['POST'])
    @cross_origin()
    def processTranslation():
        data = request.get_json()
        content = data.get("t")
        print(CGREY)
        if not silent: print(CBEIGE+"Incoming text:"+CGREY, content)
        finalResult = json.dumps(translate(ja2en, content))
        if not silent: print(CBEIGE+"Translated:"+CGREY, finalResult)
        print(CEND)
        return Response(finalResult, mimetype='text/json')

    @app.route("/", methods = ['POST'])
    @cross_origin()
    def processPost():
        data = request.get_json()
        message = data.get("message")
        content = data.get("content")

        if (message == "translate sentences"):
            print(CGREY)
            if not silent: print(CBEIGE+"Incoming text:"+CGREY, content)
            finalResult = json.dumps(translate(ja2en, content))
            if not silent: print(CBEIGE+"Translated:"+CGREY, finalResult)
            print(CEND)
            return finalResult

        if (message == "batch"):
            result = batchTranslate(ja2en, content)
            return json.dumps(result)

        if (message == "status"):
            return json.dumps(status)

        if (message == "close server"):
            #shutdown_server()
            print("Received a request to shut down the server.")
            print("SHUTING DOWN SERVER!")
            os.kill(os.getpid(), signal.SIGINT)


    app.run(host=host, port=port)
    print("Server is running")


def getHelp():
    print('''
Sugoi Translator with Fairseq
Mod for Translator++
=============================

CLI Args:
    -h / --help
        Displays this message

    -n / --host [hostname]
        Set the host name / ip address to listen to

    -p / --port [port number]
        Set port number

    -g / --gpu
        Run on GPU mode instead of CPU

    -s / --silent
        Suppress message.

Example:
    py startServer.py -s 127.0.0.1 -p 27027
    ''')


def init():
    global selectedModel
    global silent
    global port
    global host
    global gpu

    print(CYELLOW+"Fairseq"+CEND+" with Sugoi Translator's pre-trained model. Flask server mod for Translator++")
    print("Use arg -h to display the help menu")
    print(CBLUE+"===================================================================================="+CEND)
    try:
        # Parsing argument
        arguments, values = getopt.getopt(argumentList, options, long_options)
        
        # checking each argument
        for currentArgument, currentValue in arguments:

            if currentArgument in ("-h", "--Help"):
                getHelp()
                quit()
                
            elif currentArgument in ("-s", "--silent"):
                silent = True

            elif currentArgument in ("-n", "--host"):
                host = currentValue
                
            elif currentArgument in ("-p", "--port"):
                port = currentValue

            elif currentArgument in ("-g", "--gpu"):
                gpu=True
            
            elif currentArgument in ("-m", "--model"):
                selectedModel = currentValue

    except getopt.error as err:
        # output error, and return with an error code
        print (str(err))

    processor = CYELLOW+"NO"+CEND
    if gpu: processor = CGREEN+"YES"+CEND

    print(CBEIGE,'Starting server',CYELLOW, host, CBEIGE, 'on port', CYELLOW, port, CBEIGE, 'use GPU:', processor, CEND)
    print('Selected model:', selectedModel)
    runService(host, port, gpu, silent)


if __name__ == "__main__":
    init()