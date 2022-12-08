
import sqlite3, os, sys, json
os.chdir(os.path.dirname(__file__))


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
        "info":config
    }

print(getConfiguration())
sys.exit(0)

tableName = "cache"
con = sqlite3.connect("../db/cache.db")
db = con.cursor()

db.execute("DROP TABLE IF EXISTS "+tableName)

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

db.executescript("""
BEGIN TRANSACTION;
INSERT OR IGNORE INTO cache(original, translation) VALUES("はい", "Yes");
INSERT OR IGNORE INTO cache(original, translation) VALUES("いいえ", "No");
COMMIT;
""")
db.executescript("""
BEGIN TRANSACTION;
INSERT OR IGNORE INTO cache(original, translation) VALUES
("素敵", "Beautiful"),
("優しい", "Kind");
COMMIT;
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
    
def translator_translate(texts):
    return ["Hello", "Good morning"]

def translate(translator, originalTexts):
    #translated = translator.translate(text)
    cacheInfo = loadFromCache(originalTexts)
    print("Cache info:", cacheInfo)
    if len(cacheInfo["uncached"]) == 0: return cacheInfo["cached"]

    translated = translator_translate(cacheInfo["uncached"])
    result = cacheInfo["cached"]

    translatedIndex = 0
    for cacheIndex in cacheInfo["uncachedIndexes"]:
        result[cacheIndex] = translated[translatedIndex]
        translatedIndex += 1
    
    dbAddCache(cacheInfo["uncached"], translated)
    return result


data = ["はい", "素敵", "こんにちは", "いいえ", "おはようございます", "優しい"]
translation = ["", "Hello", "", "Good morning"]
print(translate(False, data))

sys.exit(0)

dbAddCache(data, translation)
print("from cache", loadFromCache(["おはようございます"]))

cacheResult = loadFromCache(["はい", "広い", "いいえ"])
print("Cache result", cacheResult)

print("Translation", translation)



mergedResult = mergeCache(translation, cacheResult["cached"])
print("Merged result", mergedResult)
print("End of application")