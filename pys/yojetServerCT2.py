"""
MIT License

Copyright (c) 2022 Dreamsavior

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from flask import Flask
from flask import request
from flask_cors import CORS, cross_origin

import ctranslate2
import re
import time
import getopt, sys, os, json, signal, glob
import sentencepiece as spm

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

# Handle cache
import sqlite3
tableName = "cache"
con = sqlite3.connect("../db/cache.db", check_same_thread=False)
db = con.cursor()

res = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='"+tableName+"'")
if res.fetchone() is None:
    print("Table "+tableName+" is not exist! creating one.")
    db.execute("""
        CREATE TABLE IF NOT EXISTS cache (
            original TEXT PRIMARY KEY,
            translation TEXT NOT NULL,
            UNIQUE(original)
        )
    """)

def dbAddCache(originalText, translationResult):
    originalText = originalText or []
    translationResult = translationResult or []
    if "".join(originalText) == "": return
    if "".join(translationResult) == "": return
    
    valuestr = []
    values = []
    index = 0
    for line in translationResult:
        line = line or ""
        if line != "": 
            valuestr.append("(?, ?)")
            values.append(originalText[index])
            values.append(line)
        index += 1
    queryStr = """INSERT OR IGNORE INTO cache(original, translation) VALUES """+",".join(valuestr)
    db.execute(queryStr, values)
    con.commit()



def loadFromCache(keywords):
    result = []
    uncached = []
    uncachedIndexes =[]
    index = 0
    for line in keywords:
        res = db.execute("SELECT translation FROM cache WHERE original=?", [line])
        translated = res.fetchone()
        if translated is None: 
            result.append("")
            uncached.append(line)
            uncachedIndexes.append(index)
        else:
            result.append(translated[0])
        index += 1
    return {
        "cached":result,
        "uncached":uncached,
        "uncachedIndexes":uncachedIndexes
    }

def mergeCache(translationResult, cacheResult):
    translationResult = translationResult or []
    cacheResult = cacheResult or []
    if len(cacheResult) == 0: return translationResult
    result = []
    index = 0
    for line in translationResult:
        line = line or ""
        if line != "": 
            result.append(line)
        else:
            result.append(cacheResult[index] or "")
        index += 1
    return result

# end of cache handler
def parseModelId(modelId):
    modelInfo = {
        'name': 'name',
        'engine': 'fairseq',
        'version': '1.0',
        'langFrom': 'ja',
        'langTo':'en'
    }

    segm = modelId.split("-")
    modelInfo["name"] = segm[0] or "name"
    modelInfo["engine"] = segm[1] or "fairseq"
    modelInfo["version"] = segm[2] or "1.0"

    if len(segm) >= 4 :
        langList = segm[3].split("_")
        modelInfo["langFrom"] = langList[0] or "ja"
        modelInfo["langTo"] = langList[1] or "en"

    return modelInfo

def getConfiguration(configFile=""):
    if not configFile:
        configFile = "../config.json"
    if configFile == "default":
        configFile = "../config.json"

    if not os.path.isfile(configFile):
        print("Error! File", configFile, "is not exist!")
        return
    
    configString  = open(configFile, 'r', encoding="UTF-8")
    config = json.load(configString)
    return {
        "configPath": configFile,
        "info":config,
        "model":parseModelId(config['model'])
    }


#===========================================================
# APPLICATION
#===========================================================


print(CYELLOW+"YOJET SERVER with CTranslate2 ver."+ctranslate2.__version__+CEND+". Flask server mod for Translator++")
print("Server Ver. 0.4")
print("Use arg -h to display the help menu")
print(CBLUE+"===================================================================================="+CEND)
#===========================================================
# INITIALIATION
#===========================================================
host='0.0.0.0'
port=14366
gpu= False
device = "cpu" # cuda or cpu
intra_threads=4
inter_threads=1
beam_size=5
repetition_penalty=3
modelDir = "models/sugoi-ct2-levi/"
sp_source_model = "models/sp_model/spm.ja.nopretok.model"
sp_target_model = "models/sp_model/spm.en.nopretok.model"
useCache = True
silent = False
disable_unk = False

def applyConfiguration(configFile=""):
    print("Current dir", os.getcwd())
    print(getConfiguration())
    global host
    global port
    global modelDir
    global sp_source_model
    global sp_target_model
    global device

    configuration = getConfiguration(configFile)
    if configuration is None: return
    print("Config is:", configuration)
    config = configuration["info"]

    host = config['host']
    port = config['port']
    
    if config['useGpu']: device = "cuda"

    try:
        thePath = glob.glob('../models/'+config['model']+'/**/*.bin', recursive=True)[0]
        modelFileName=os.path.basename(thePath)
        modelDir=os.path.dirname(thePath)
        print("Model filename : "+modelFileName)
        print("Model dir : "+modelDir)

        sp_source_model = glob.glob('../models/'+config['model']+'/**/spm.'+configuration["model"]["langFrom"]+'.*.model', recursive=True)[0]
        sp_target_model = glob.glob('../models/'+config['model']+'/**/spm.'+configuration["model"]["langTo"]+'.*.model', recursive=True)[0]

    except:
        print("no model found")



def getHelp():
    print('''
Sugoi Translator with CT2
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

    -b / --beam_size
        Control the beam size. Default is 3. Increase for better quality. Decrese for faster translation.

    -r / --repetition_penalty
        Control repetition penalty. Default is 3. Increase to suppress repetition.

    -u / --disable_unk
        Disable unknown token

    -s / --silent
        Suppress message.

Example:
    py startServer.py -s 127.0.0.1 -p 27027
    py startServer.py -g
    ''')

#===========================================================
# HANDLING ARGUMENTS
#===========================================================
# Remove 1st argument from the
# list of command line arguments
argumentList = sys.argv[1:]
 
# Options
options = "hsgn:p:b:r:c:u"
 
# Long options
long_options = ["help", "silent", "gpu", "host =", "port =", "beam_size =", "repetition_penalty =", "config =", "disable_unk"]
status = "ready"

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
            device="cuda"
        elif currentArgument in ("-b", "--beam_size"):
            beam_size = int(currentValue)
            
        elif currentArgument in ("-r", "--repetition_penalty"):
            repetition_penalty = int(currentValue)

        elif currentArgument in ("-u", "--disable_unk"):
            disable_unk = True        
        elif currentArgument in ("-c", "--config"):
            #setConfiguration(currentValue)
            applyConfiguration()


except getopt.error as err:
    # output error, and return with an error code
    print (str(err))
    print(CBLUE+"===================================================================================="+CEND)
    getHelp()
    quit()


#===========================================================
# MAIN APPLICATION
#===========================================================
print(CGREEN,'Starting server', host, 'on port', port, 'device:', CYELLOW+device, CEND)

translator = ctranslate2.Translator(modelDir, device=device, intra_threads=intra_threads, inter_threads=inter_threads)

def tokenizeBatch(text, sp_source_model):
    sp = spm.SentencePieceProcessor(sp_source_model)
    if isinstance(text, list):
        return sp.encode(text, out_type=str)
    else:
        return [sp.encode(text, out_type=str)]


def detokenizeBatch(text, sp_target_model):
    sp = spm.SentencePieceProcessor(sp_target_model)
    translation = sp.decode(text)
    return translation

def doTranslate(originalTexts):
    if (ctranslate2.__version__ == "2.22.0"):
        translatedToken = translator.translate_batch(
            source=tokenizeBatch(originalTexts, sp_source_model), 
            normalize_scores=True,
            allow_early_exit=False, 
            beam_size=beam_size, 
            num_hypotheses=1, 
            return_alternatives=False, 
            disable_unk=True, 
            replace_unknowns=False, 
            no_repeat_ngram_size=repetition_penalty
        )
    else:
        translatedToken = translator.translate_batch(
            source=tokenizeBatch(originalTexts, sp_source_model), 
            normalize_scores=True,
            allow_early_exit=False, 
            beam_size=beam_size, 
            num_hypotheses=1, 
            return_alternatives=False, 
            disable_unk=disable_unk, 
            replace_unknowns=False, 
            repetition_penalty=repetition_penalty
        )            
    #translated = translator.translate_batch(source=tokenizeBatch(content, sp_source_model), normalize_scores=True, allow_early_exit=False, beam_size=beam_size, num_hypotheses=1, return_alternatives=False, disable_unk=False, replace_unknowns=False, repetition_penalty=repetition_penalty)
    return detokenizeBatch([ff[0]["tokens"] for ff in translatedToken], sp_target_model)
if useCache:
    def translate(originalTexts):
        cacheInfo = loadFromCache(originalTexts)
        print("Cache info:", cacheInfo)
        if len(cacheInfo["uncached"]) == 0: return cacheInfo["cached"]

        translated = doTranslate(cacheInfo["uncached"])
        result = cacheInfo["cached"]

        translatedIndex = 0
        for cacheIndex in cacheInfo["uncachedIndexes"]:
            result[cacheIndex] = translated[translatedIndex]
            translatedIndex += 1
        
        dbAddCache(cacheInfo["uncached"], translated)   
        return result 
else:
    def translate(originalTexts):
        return doTranslate(originalTexts)



app = Flask(__name__)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

@app.route("/", methods = ['POST','GET'])
@cross_origin()

def sendSugoi():
    tic = time.perf_counter()
    data = request.get_json(True)
    message = data.get("message")
    content = data.get("content")

    if (message == "close server"):
        shutdown_server()
        return

    if (message == "translate sentences"):
        textlist = []
        print(CGREY)
        if not silent: print(CBEIGE+"Incoming text:"+CGREY, content)
        finalResult = translate(content)
        if not silent: print(CBEIGE+"Translated:"+CGREY, finalResult)
        print(CEND)
        return json.dumps(finalResult)

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

if __name__ == "__main__":
    app.run(host=host, port=port)