# YOJET
YOJET or **Y**our **O**wn **J**apanese **E**nglish **T**ranslator  is a free Japanese-English translation server. The aim of this application is to provide a hassle free Japanese-English translator service with a web translator and  REST API over HTTP.

More about YOJET:
https://dreamsavior.net/yojet/

# API
### To translate some texts
```javaScript
var req = await fetch(`http://127.0.0.1:14341/translate`, {
	method : "POST",
	body : JSON.stringify({t: [`こんにちは`, `よろしくお願いします。`]}),
	headers : {'Content-Type': 'application/json'}
})
await req.json();
```
Result:
```JSON
[
  "Hello. Hello.",
  "I look forward to working with you."
]
```

## To batch translate JSON
Maybe you need to translate mega or gigabytes of text. Maybe translating it part by part via the HTTP protocol is not a good idea as there will be a lot of process overhead.
In this case you can collect all the text that needs to be translated into one file, and YOJET will translate it for you.
### Example
Create a job file with the following format:
```
{"text":["こんにちは", "こんばんは。"], "note":"you can translate an array of texts"}
{"text":"お疲れ様でした", "info":"or you can translate a single of text"}
{"text":"ご苦労さん", "Please note that":"Each line is one JSON object."}
{"text":"毎日私はご飯を食べます", "otherParameter": {"info":"YOJET will translate line by line so no matter how big the file you have it won't have a big impact on your computer's RAM."}}
{"text":"何は同年もっともそうした入会屋というのの上が上るたです", "otherparam":"3"}
```
Note that:

 - One line represents one JSON object.
 - This file does not consist of one JSON object, but many JSON objects separated by new lines.
 - By default YOJET will translate properties named `text` .
 - You can include any property on the JSON subset, but please note that the result of the translation will be put into the `translated` property. Any existing value will be overwritten by the translation result.

Send the request with `f` parameter referring to the path of the job file:
```javaScript
var req = await fetch(`http://127.0.0.1:14377/batch`, {
	method : "POST",
	body : JSON.stringify({f: "D:/test/batch/job.txt"}),
	headers : {'Content-Type': 'application/json'}
})
await req.json();
```

The result file will be on the same path with the job file with `.translated` extension.
The content of the result file from this example:
```
{"text":["こんにちは", "こんばんは。"], "translated": ["Hello.", "Good evening."], "note":"you can translate an array of texts"}
{"text":"お疲れ様でした", "translated": "Thanks for your hard work.", "info":"or you can translate a single of text"}
{"text":"ご苦労さん", "translated": "Thanks for your hard work.", "Please note that":"Each line is one JSON object."}
{"text":"毎日私はご飯を食べます", "translated": "I eat every day.", "otherParameter": {"info":"YOJET will translate line by line so no matter how big the file you have it won't have a big impact on your computer's RAM."}}
{"text":"何は同年もっともそうした入会屋というのの上が上るたです", "translated": "What's more, in the same year, that's one of the best admissions places in the world.", "otherparam":"3"}
```

Note that
The unicode and non ASCII character may be escaped in the result file. (Example, Store Unicode **string  `ø`  as  `\u00f8`  in JSON**)